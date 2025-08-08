"""
Python MCP Client for Advanced Scripting
Allows Python scripts to connect to the same MCP server and fetch data
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, ToolUseBlock, TextBlock


class PythonMCPClient:
    """Python client for programmatic MCP server interaction"""
    
    def __init__(self, mcp_config_path: str = "config/mcp_config.json"):
        """Initialize the Python MCP client"""
        self.config_path = Path(mcp_config_path)
        self._load_config()
        self.query_cache = {}
        
    def _load_config(self):
        """Load MCP server configuration"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"MCP config not found at {self.config_path}")
        
        with open(self.config_path) as f:
            config = json.load(f)
            self.mcp_servers = config.get('mcpServers', {})
    
    async def call_tool(self, 
                       tool_name: str, 
                       params: Dict[str, Any],
                       use_cache: bool = True) -> Optional[Any]:
        """
        Call an MCP tool programmatically
        
        Args:
            tool_name: Name of the MCP tool to call
            params: Parameters for the tool
            use_cache: Whether to use cached results
            
        Returns:
            The result from the tool call
        """
        # Check cache first
        cache_key = f"{tool_name}_{json.dumps(params, sort_keys=True)}"
        if use_cache and cache_key in self.query_cache:
            print(f"Using cached result for {tool_name}")
            return self.query_cache[cache_key]
        
        # Configure options
        options = ClaudeCodeOptions(
            system_prompt="You are a data fetching assistant. Execute the requested tool and return the result.",
            mcp_servers=self.mcp_servers,
            allowed_tools=[tool_name],
            max_turns=5
        )
        
        # Create prompt
        prompt = f"Please execute the tool {tool_name} with these parameters: {json.dumps(params)}"
        
        result = None
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name == tool_name:
                        # Tool was called, wait for result in next message
                        pass
                    elif isinstance(block, TextBlock) and result is None:
                        # Try to extract result from text
                        try:
                            # Look for JSON in the response
                            text = block.text
                            if '{' in text and '}' in text:
                                start = text.find('{')
                                end = text.rfind('}') + 1
                                result = json.loads(text[start:end])
                        except:
                            result = block.text
        
        # Cache the result
        if result is not None and use_cache:
            self.query_cache[cache_key] = result
        
        return result
    
    async def get_solana_price(self, token_address: str = "So11111111111111111111111111111111111111112") -> Optional[float]:
        """
        Get current Solana price using MCP
        
        Args:
            token_address: Solana token address
            
        Returns:
            Current price or None if failed
        """
        # First search for the server
        servers = await self.call_tool("mcp__fluora__searchFluora", {})
        
        if not servers:
            print("Failed to find MCP servers")
            return None
        
        # Get payment method
        payment_info = await self.call_tool("mcp__fluora__callServerTool", {
            "serverId": "9f2e4fe1-dc04-4ed1-bab4-0f374cb9f8a7",
            "mcpServerUrl": "http://localhost:80",
            "toolName": "payment-method",
            "args": {}
        })
        
        if not payment_info:
            print("Failed to get payment method")
            return None
        
        # Make purchase
        result = await self.call_tool("mcp__fluora__callServerTool", {
            "serverId": "9f2e4fe1-dc04-4ed1-bab4-0f374cb9f8a7",
            "mcpServerUrl": "http://localhost:80", 
            "toolName": "make-purchase",
            "args": {
                "itemId": "solanapricecurrent",
                "params": {"token_address": token_address},
                "paymentMethod": "USDC_BASE_SEPOLIA",
                "itemPrice": 0.001,
                "serverWalletAddress": payment_info.get("walletAddress", "")
            }
        })
        
        # Extract price from result
        if result and isinstance(result, dict):
            return result.get("price")
        
        return None
    
    async def get_batch_prices(self, token_addresses: List[str]) -> Dict[str, float]:
        """
        Get prices for multiple tokens
        
        Args:
            token_addresses: List of token addresses
            
        Returns:
            Dictionary mapping token address to price
        """
        prices = {}
        
        for address in token_addresses:
            price = await self.get_solana_price(address)
            if price:
                prices[address] = price
            await asyncio.sleep(1)  # Rate limiting
        
        return prices
    
    def save_cache(self, filepath: str = "knowledge/mcp_cache.json"):
        """Save query cache to disk"""
        cache_dir = Path(filepath).parent
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(self.query_cache, f, indent=2)
    
    def load_cache(self, filepath: str = "knowledge/mcp_cache.json"):
        """Load query cache from disk"""
        cache_path = Path(filepath)
        if cache_path.exists():
            with open(cache_path) as f:
                self.query_cache = json.load(f)


# Convenience functions for scripts
async def fetch_solana_data_for_training():
    """
    Fetch Solana market data suitable for model training
    
    Returns:
        Dictionary with training data
    """
    client = PythonMCPClient()
    
    # Define tokens to track
    tokens = {
        "SOL": "So11111111111111111111111111111111111111112",
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        # Add more tokens as needed
    }
    
    # Fetch current prices
    prices = await client.get_batch_prices(list(tokens.values()))
    
    # Create training data structure
    training_data = {
        "timestamp": datetime.now().isoformat(),
        "prices": {},
        "features": {}
    }
    
    for name, address in tokens.items():
        if address in prices:
            training_data["prices"][name] = prices[address]
            
            # Add derived features
            training_data["features"][f"{name}_log_price"] = np.log(prices[address]) if prices[address] > 0 else 0
    
    # Save cache for future use
    client.save_cache()
    
    return training_data


# Example usage
if __name__ == "__main__":
    import numpy as np
    
    async def main():
        # Example 1: Direct tool call
        client = PythonMCPClient()
        result = await client.call_tool("mcp__fluora__searchFluora", {})
        print("Available servers:", result)
        
        # Example 2: Get SOL price
        price = await client.get_solana_price()
        print(f"Current SOL price: ${price}")
        
        # Example 3: Fetch training data
        data = await fetch_solana_data_for_training()
        print("Training data:", json.dumps(data, indent=2))
    
    asyncio.run(main())
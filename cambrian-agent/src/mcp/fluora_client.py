"""
Fluora MCP Client for making real monetized requests
"""

import json
import subprocess
import asyncio
from typing import Dict, Optional, Any
from pathlib import Path

import structlog

logger = structlog.get_logger()


class FluoraMCPClient:
    """Client for making requests through the Fluora monetized MCP server"""
    
    def __init__(self, mcp_config_path: str = "config/mcp_config.json"):
        # Load MCP configuration
        with open(mcp_config_path) as f:
            self.mcp_config = json.load(f)
        
        self.fluora_config = self.mcp_config.get('mcpServers', {}).get('fluora', {})
        if not self.fluora_config:
            raise ValueError("Fluora MCP server not found in configuration")
        
        logger.info("Initialized Fluora MCP client", 
                   command=self.fluora_config.get('command'),
                   api_url=self.fluora_config.get('env', {}).get('FLUORA_API_URL'))
    
    async def make_purchase(self, item_id: str, params: Dict, 
                          payment_method: str = "USDC_BASE_SEPOLIA",
                          item_price: float = 0.001,
                          server_wallet_address: str = "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3") -> Optional[Dict]:
        """
        Make a purchase through the monetized MCP
        
        Args:
            item_id: The Cambrian API endpoint ID (e.g., "solanapricecurrent")
            params: Parameters for the API call
            payment_method: Payment method to use
            item_price: Price in USDC
            server_wallet_address: Recipient wallet address
        
        Returns:
            The API response data or None if failed
        """
        
        # Prepare the MCP request
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "mcp__fluora__make-purchase",
            "params": {
                "itemId": item_id,
                "params": params,
                "itemPrice": item_price,
                "paymentMethod": payment_method,
                "serverWalletAddress": server_wallet_address
            },
            "id": 1
        }
        
        logger.info("Making MCP purchase request",
                   item_id=item_id,
                   params=params,
                   payment_method=payment_method,
                   price=item_price)
        
        try:
            # Execute the MCP command
            cmd = [self.fluora_config['command']] + self.fluora_config['args']
            
            # Set up environment
            env = dict(self.fluora_config.get('env', {}))
            
            # Create the process
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            # Send the request
            request_data = json.dumps(mcp_request).encode()
            stdout, stderr = await process.communicate(input=request_data)
            
            if stderr:
                logger.error("MCP error output", stderr=stderr.decode())
            
            # Parse response
            if stdout:
                response = json.loads(stdout.decode())
                logger.info("MCP response received", 
                           has_result='result' in response,
                           has_error='error' in response)
                
                if 'result' in response:
                    return response['result']
                elif 'error' in response:
                    logger.error("MCP request failed", error=response['error'])
                    return None
            
            return None
            
        except Exception as e:
            logger.error("Failed to execute MCP request", 
                        error=str(e),
                        item_id=item_id)
            return None
    
    async def get_token_price(self, token_address: str, symbol: str = "") -> Optional[Dict]:
        """
        Get current token price via MCP
        
        Args:
            token_address: Solana token address
            symbol: Token symbol for logging
        
        Returns:
            Price data or None if failed
        """
        logger.info(f"Fetching {symbol} price via MCP", token_address=token_address)
        
        result = await self.make_purchase(
            item_id="solanapricecurrent",
            params={"token_address": token_address}
        )
        
        if result:
            logger.info(f"Received {symbol} price data", 
                       has_data=bool(result),
                       payment_success='payment' in str(result).lower())
        
        return result
    
    async def list_purchasable_items(self) -> Optional[Dict]:
        """List available items from the MCP server"""
        
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "mcp__fluora__list-purchasable-items",
            "params": {},
            "id": 1
        }
        
        try:
            cmd = [self.fluora_config['command']] + self.fluora_config['args']
            env = dict(self.fluora_config.get('env', {}))
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )
            
            request_data = json.dumps(mcp_request).encode()
            stdout, stderr = await process.communicate(input=request_data)
            
            if stdout:
                response = json.loads(stdout.decode())
                if 'result' in response:
                    return response['result']
            
            return None
            
        except Exception as e:
            logger.error("Failed to list items", error=str(e))
            return None
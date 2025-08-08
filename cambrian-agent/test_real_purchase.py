#!/usr/bin/env python3
"""
Test REAL MCP purchase
"""

import anyio
import os
import json
from dotenv import load_dotenv
from claude_code_sdk import query, ClaudeCodeOptions

load_dotenv()

async def test_real_purchase():
    """Test making a REAL MCP purchase"""
    
    # Load MCP config
    with open('config/mcp_config.json') as f:
        mcp_config = json.load(f)
    
    # Prompt to make a real purchase
    prompt = """Make a REAL purchase for current SOL price data using these exact steps:

1. Use mcp__fluora__callServerTool with these exact parameters:
   {
     "serverId": "monetized-blockchain-data-provider",
     "mcpServerUrl": "https://mcp.server.fluora.to/monetized-blockchain-data-provider",
     "toolName": "make-purchase",
     "args": {
       "itemId": "solanapricecurrent",
       "params": {"token_address": "So11111111111111111111111111111111111111112"},
       "paymentMethod": "USDC_BASE_SEPOLIA",
       "itemPrice": 0.001,
       "serverWalletAddress": "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3"
     }
   }

This is a REAL purchase that will cost 0.001 USDC on Base Sepolia testnet.
After the purchase, show me the price data you received."""
    
    # Configure with MCP
    options = ClaudeCodeOptions(
        mcp_servers=mcp_config['mcpServers'],
        allowed_tools=[
            "mcp__fluora__listServerTools", 
            "mcp__fluora__callServerTool",
            "mcp__fluora__searchFluora",
            "ListMcpResourcesTool"
        ],
        max_turns=5
    )
    
    print("Testing REAL MCP purchase...")
    print("This will cost 0.001 USDC on Base Sepolia!")
    print()
    
    # Run query
    async for message in query(prompt=prompt, options=options):
        print(f"Message type: {type(message).__name__}")
        
        # Print details based on message type
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'name'):
                    print(f"  Tool: {block.name}")
                    if hasattr(block, 'input'):
                        print(f"  Input: {json.dumps(block.input, indent=2)}")
                elif hasattr(block, 'text'):
                    print(f"  Text: {block.text[:200]}...")
                elif hasattr(block, 'content'):
                    print(f"  Result: {str(block.content)[:300]}...")

async def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: No API key")
        return
    
    await test_real_purchase()

if __name__ == "__main__":
    anyio.run(main)
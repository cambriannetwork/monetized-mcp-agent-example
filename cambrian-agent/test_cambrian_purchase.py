#!/usr/bin/env python3
"""
Test REAL Cambrian API purchase through fluora MCP
"""

import anyio
import os
import json
from dotenv import load_dotenv
from claude_code_sdk import query, ClaudeCodeOptions

load_dotenv()

async def test_cambrian_purchase():
    """Test making a REAL purchase from Cambrian API"""
    
    # Load MCP config
    with open('config/mcp_config.json') as f:
        mcp_config = json.load(f)
    
    # Prompt to make a real purchase
    prompt = """Using the fluora MCP server, make a REAL purchase from the Cambrian API:

1. First search for available servers using mcp__fluora__searchFluora
2. Find the Cambrian API server (usually at https://mcp.rickycambrian.org/monetized)
3. Use mcp__fluora__callServerTool to call the 'pricing-listing' tool to see available items
4. Then use mcp__fluora__callServerTool to call the 'make-purchase' tool to buy SOL price data

Use the correct serverId and mcpServerUrl from the search results.
This is a REAL purchase that will cost 0.001 USDC on Base Sepolia testnet.
Show me the price data you receive."""
    
    # Configure with MCP
    options = ClaudeCodeOptions(
        mcp_servers=mcp_config['mcpServers'],
        allowed_tools=[
            "mcp__fluora__searchFluora",
            "mcp__fluora__callServerTool",
            "mcp__fluora__listServerTools"
        ],
        max_turns=10  # More turns to complete the full flow
    )
    
    print("=== CAMBRIAN API REAL PURCHASE TEST ===")
    print("This will make a REAL purchase costing 0.001 USDC!")
    print("Monitor transactions at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
    print()
    
    # Track what happens
    purchases_made = []
    
    # Run query
    async for message in query(prompt=prompt, options=options):
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'name') and block.name == 'mcp__fluora__callServerTool':
                    input_data = block.input if hasattr(block, 'input') else {}
                    tool_name = input_data.get('toolName', '')
                    
                    print(f"\n>>> Calling {tool_name}")
                    print(f"    Server: {input_data.get('mcpServerUrl', 'unknown')}")
                    
                    if tool_name == 'make-purchase':
                        args = input_data.get('args', {})
                        print(f"    Item: {args.get('itemId', 'unknown')}")
                        print(f"    Price: {args.get('itemPrice', 'unknown')} USDC")
                        purchases_made.append(args)
                        
                elif hasattr(block, 'text') and len(block.text) > 0:
                    # Only print non-empty text
                    preview = block.text[:150].replace('\n', ' ')
                    if preview.strip():
                        print(f"\nClaude: {preview}...")
    
    # Summary
    print(f"\n\n=== PURCHASE SUMMARY ===")
    print(f"Total purchases attempted: {len(purchases_made)}")
    if purchases_made:
        print("\nPurchases:")
        for i, p in enumerate(purchases_made, 1):
            print(f"  {i}. {p.get('itemId', 'unknown')} - ${p.get('itemPrice', 0)} USDC")
        print(f"\nCheck blockchain: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
    else:
        print("No purchases were made.")

async def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not found")
        return
    
    await test_cambrian_purchase()

if __name__ == "__main__":
    anyio.run(main)
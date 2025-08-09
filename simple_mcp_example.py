#!/usr/bin/env python3
"""
Simple MCP Example - Make a single purchase from Cambrian API

This is a minimal example showing how to:
1. Connect to the fluora MCP server
2. Find the Cambrian API
3. Make a real purchase (costs 0.001 USDC)
4. Get Solana price data

Prerequisites:
- ANTHROPIC_API_KEY in .env file
- fluora-mcp installed (npm install -g fluora-mcp)
- Wallet configured in ~/.fluora/wallets.json
- Wallet funded with USDC on Base Sepolia

See docs/SETUP.md for detailed instructions.
"""

import anyio
import os
import json
from dotenv import load_dotenv
from claude_code_sdk import query, ClaudeCodeOptions

# Load environment variables
load_dotenv()


async def get_solana_price():
    """Make a real purchase to get current SOL price"""
    
    # Load MCP configuration
    with open('config/mcp_config.json') as f:
        mcp_config = json.load(f)
    
    # System prompt explaining the task
    system_prompt = """You are making a REAL purchase from the Cambrian API.
This will cost 0.001 USDC on Base Sepolia testnet."""
    
    # Configure Claude with MCP server
    options = ClaudeCodeOptions(
        system_prompt=system_prompt,
        mcp_servers=mcp_config['mcpServers'],
        allowed_tools=[
            "mcp__fluora__exploreServices",
            "mcp__fluora__getServiceDetails",
            "mcp__fluora__callServiceTool"
        ],
        max_turns=10
    )
    
    # Prompt with clear instructions
    prompt = """Make a REAL purchase to get the current SOL price:

1. Use mcp__fluora__exploreServices to find the Cambrian API server
2. Use mcp__fluora__callServiceTool to call 'payment-methods' to get wallet address
3. Use mcp__fluora__callServiceTool to call 'make-purchase' with:
   - itemId: "solanapricecurrent"
   - params: {"token_address": "So11111111111111111111111111111111111111112"}
   - paymentMethod: "USDC_BASE_SEPOLIA"
   - itemPrice: 0.001

Show me the price you get."""
    
    print("🚀 Making REAL purchase from Cambrian API...")
    print("💰 This will cost 0.001 USDC\n")
    
    # Execute the query
    async for message in query(prompt=prompt, options=options):
        # Messages are automatically printed by Claude SDK
        pass
    
    print("\n✅ Purchase complete!")
    print("🔗 Check transaction: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")


async def main():
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file")
        return
    
    await get_solana_price()


if __name__ == "__main__":
    print("=== Simple Cambrian API MCP Example ===\n")
    anyio.run(main)
#!/usr/bin/env python3
"""
Test REAL MCP calls using Claude SDK
"""

import asyncio
import json
from datetime import datetime

import anyio
from claude_code_sdk import query, ClaudeCodeOptions

async def test_real_mcp_call():
    """Make a REAL MCP purchase"""
    
    print("=" * 60)
    print("Testing REAL MCP Purchase")
    print("=" * 60)
    
    # This will make an ACTUAL purchase
    prompt = """Make a REAL monetized MCP purchase using the fluora server.

Use the mcp__fluora__make-purchase tool with these EXACT parameters:
{
  "itemId": "solanapricecurrent",
  "params": {
    "token_address": "So11111111111111111111111111111111111111112"
  },
  "paymentMethod": "USDC_BASE_SEPOLIA",
  "itemPrice": 0.001,
  "serverWalletAddress": "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3"
}

This should result in a real transaction on Base Sepolia.
Show me the complete response."""
    
    options = ClaudeCodeOptions(
        max_turns=1,
        allowed_tools=["mcp__fluora__make-purchase"],
        system_prompt="Make the MCP purchase exactly as specified."
    )
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Making REAL MCP call...")
    print("This will cost 0.001 USDC on Base Sepolia")
    print("Transaction should appear at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
    print()
    
    messages = []
    async for message in query(prompt=prompt, options=options):
        messages.append(message)
        if hasattr(message, 'content'):
            print(f"Response: {message.content}")
    
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] MCP call completed")
    print(f"Total messages: {len(messages)}")

if __name__ == "__main__":
    print("Starting REAL MCP test...")
    print("This will make an actual paid transaction!")
    print()
    
    anyio.run(test_real_mcp_call)
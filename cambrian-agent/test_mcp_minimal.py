#!/usr/bin/env python3
"""
Minimal test for MCP functionality
"""

import os
os.environ["ANTHROPIC_API_KEY"] = "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"

import anyio
from claude_code_sdk import query, ClaudeCodeOptions

async def test():
    options = ClaudeCodeOptions(
        mcp_config="../config/mcp_config.json",
        allowed_tools=["mcp__fluora__make-purchase"],
        verbose=True
    )
    
    prompt = """Use the mcp__fluora__make-purchase tool to buy SOL price data.
Parameters:
- itemId: "solanapricecurrent"
- params: {"token_address": "So11111111111111111111111111111111111111112"}
- paymentMethod: "USDC_BASE_SEPOLIA"
- itemPrice: 0.001
- serverWalletAddress: "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3"
"""
    
    print("Attempting MCP purchase...")
    async for message in query(prompt=prompt, options=options):
        print(f"\nGot: {type(message).__name__}")

anyio.run(test)
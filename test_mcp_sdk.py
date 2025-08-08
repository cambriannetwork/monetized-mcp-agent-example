#!/usr/bin/env python3

import anyio
import json
from claude_code_sdk import query, ClaudeCodeOptions, Message

async def test_monetized_mcp():
    """Test the monetized MCP using Claude Code SDK"""
    
    print("Testing monetized MCP connection via Claude Code SDK...")
    
    # Configure options to allow MCP tools
    options = ClaudeCodeOptions(
        max_turns=1,
        allowed_tools=["mcp__fluora__make-purchase", "mcp__fluora__list-purchasable-items"],
        system_prompt="You are testing the monetized MCP connection. Use the fluora MCP server to make a purchase."
    )
    
    # Test prompt
    prompt = """Use the fluora MCP server to:
    1. First list available purchasable items
    2. Then purchase the current SOL price data using these parameters:
       - itemId: solanapricecurrent
       - token_address: So11111111111111111111111111111111111111112
       - paymentMethod: USDC_BASE_SEPOLIA
       - itemPrice: 0.001
       - serverWalletAddress: 0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3
    
    Show me the raw response data."""
    
    messages = []
    async for message in query(prompt=prompt, options=options):
        messages.append(message)
        print(f"\nMessage class: {type(message).__name__}")
        
        # Handle different message types
        if hasattr(message, 'content'):
            print(f"Content: {message.content}")
        
        # Check for different attributes based on message type
        if hasattr(message, 'tool_use'):
            print(f"Tool use detected")
        
        # Print all attributes for debugging
        print(f"Message attributes: {[attr for attr in dir(message) if not attr.startswith('_')]}")
    
    return messages

if __name__ == "__main__":
    anyio.run(test_monetized_mcp)
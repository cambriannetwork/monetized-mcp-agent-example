#!/usr/bin/env python3
"""
Test script to verify MCP tools are available
"""

import anyio
import os
from dotenv import load_dotenv
from claude_code_sdk import query, ClaudeCodeOptions

load_dotenv()

async def test_mcp_tools():
    """Test if fluora MCP tools are available"""
    
    print("Testing MCP tool availability...")
    
    # Simple prompt to list available tools
    prompt = "List all available MCP tools from the fluora server using mcp__fluora__list-purchasable-items"
    
    options = ClaudeCodeOptions(
        mcp_config="../config/mcp_config.json",
        allowed_tools=[
            "mcp__fluora__list-purchasable-items"
        ],
        max_turns=1,
        verbose=True
    )
    
    print("\nAttempting to use mcp__fluora__list-purchasable-items...")
    
    tool_called = False
    async for message in query(prompt=prompt, options=options):
        print(f"\nMessage type: {type(message).__name__}")
        if hasattr(message, 'content'):
            for block in message.content:
                print(f"  Block type: {type(block).__name__}")
                if hasattr(block, 'name'):
                    print(f"  Tool: {block.name}")
                    tool_called = True
                if hasattr(block, 'text'):
                    print(f"  Text: {block.text[:100]}...")
    
    if tool_called:
        print("\n✅ MCP tools are accessible!")
    else:
        print("\n❌ MCP tools were not called - check configuration")

if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set")
    else:
        anyio.run(test_mcp_tools)
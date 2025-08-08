#!/usr/bin/env python3
"""
SIMPLE test to verify MCP works
"""

import anyio
import os
import json
from dotenv import load_dotenv
from claude_code_sdk import query, ClaudeCodeOptions

load_dotenv()

async def test_mcp():
    """Simple MCP test"""
    
    # Load MCP config
    with open('config/mcp_config.json') as f:
        mcp_config = json.load(f)
    
    # Simple prompt
    prompt = """Search for available Cambrian API endpoints by calling the searchFluora tool with a query like 'Solana price' or 'token data'"""
    
    # Configure with MCP
    options = ClaudeCodeOptions(
        mcp_servers=mcp_config['mcpServers'],
        allowed_tools=["mcp__fluora__searchFluora"],
        max_turns=2
    )
    
    print("Testing MCP connection...")
    print(f"Allowed tools: {options.allowed_tools}")
    print()
    
    # Run query
    async for message in query(prompt=prompt, options=options):
        print(f"Got message: {type(message).__name__}")
        
        # Print any tool use
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'name'):
                    print(f"  Tool called: {block.name}")
                if hasattr(block, 'text'):
                    print(f"  Text: {block.text[:100]}...")

async def main():
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: No API key")
        return
    
    await test_mcp()

if __name__ == "__main__":
    anyio.run(main)
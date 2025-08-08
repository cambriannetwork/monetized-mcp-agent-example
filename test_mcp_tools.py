#!/usr/bin/env python3
"""
Test script to verify MCP tools are available and working
"""

import asyncio
import json
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, TextBlock, ToolUseBlock

async def test_mcp_tools():
    """Test if MCP tools are available"""
    
    # Load MCP config
    with open('config/mcp_config.json') as f:
        mcp_config = json.load(f)
    
    # Configure options
    options = ClaudeCodeOptions(
        system_prompt="You are testing MCP tool availability.",
        mcp_servers=mcp_config['mcpServers'],
        allowed_tools=[
            "mcp__fluora__searchFluora",
            "mcp__fluora__listServerTools", 
            "mcp__fluora__callServerTool"
        ],
        max_turns=3
    )
    
    # Simple prompt to test tool availability
    prompt = """Please use the mcp__fluora__searchFluora tool to search for servers.
Just call the tool with an empty input {} to list all available servers."""
    
    print("Testing MCP tools availability...")
    print("=" * 60)
    
    tool_used = False
    error_occurred = False
    
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude says: {block.text}")
                elif isinstance(block, ToolUseBlock):
                    print(f"\n🔧 Tool used: {block.name}")
                    print(f"   Input: {block.input}")
                    if block.name.startswith("mcp__fluora"):
                        tool_used = True
        
        # Check for errors in the response
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'content') and isinstance(block.content, str):
                    if "permission" in block.content.lower() or "error" in block.content.lower():
                        error_occurred = True
                        print(f"\n❌ Error: {block.content}")
    
    print("\n" + "=" * 60)
    print("Test Results:")
    print(f"✓ MCP tool was used: {tool_used}")
    print(f"✓ No errors occurred: {not error_occurred}")
    
    if not tool_used:
        print("\n⚠️  MCP tools may not be properly configured!")
        print("Check that:")
        print("1. fluora-mcp is installed: npm list -g fluora-mcp")
        print("2. The MCP server can start: fluora-mcp")
        print("3. Your ANTHROPIC_API_KEY is set")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
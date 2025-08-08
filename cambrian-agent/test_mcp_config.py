#!/usr/bin/env python3
"""Test MCP configuration"""

from claude_code_sdk import ClaudeCodeOptions
import json

# Load the MCP config
with open('config/mcp_config.json') as f:
    mcp_config = json.load(f)

print("MCP Config loaded:")
print(json.dumps(mcp_config, indent=2))

# Try different ways to configure MCP
print("\n1. Testing mcp_servers parameter with dict:")
try:
    options = ClaudeCodeOptions(
        mcp_servers={"fluora": {"command": "test"}},
        allowed_tools=["mcp__fluora__make-purchase"]
    )
    print("✓ mcp_servers dict works")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n2. Testing mcp_servers with full config:")
try:
    options = ClaudeCodeOptions(
        mcp_servers=mcp_config['mcpServers'],
        allowed_tools=["mcp__fluora__make-purchase"]
    )
    print("✓ Full config works")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n3. Checking ClaudeCodeOptions attributes:")
print(f"mcp_servers type hint: {ClaudeCodeOptions.__annotations__.get('mcp_servers', 'Not found')}")
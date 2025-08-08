#!/usr/bin/env python3
"""
Direct test of MCP using the example request format
"""

import requests
import json

# Using the exact example request format provided
mcp_request = {
    "args": {
        "itemId": "solanapricecurrent",
        "params": {
            "token_address": "So11111111111111111111111111111111111111112"
        },
        "itemPrice": 0.001,
        "paymentMethod": "USDC_BASE_SEPOLIA",
        "serverWalletAddress": "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3"
    },
    "serverId": "9f2e4fe1-dc04-4ed1-bab4-0f374cb9f8a7",
    "toolName": "make-purchase",
    "mcpServerUrl": "https://mcp.rickycambrian.org/monetized"
}

print("Testing direct MCP request...")
print(f"Request: {json.dumps(mcp_request, indent=2)}")
print()

# The response format shown was:
# {"content":[{"type":"text","text":"..."}],"payment":{"paymentMessage":"..."}}

print("This is the exact format that should trigger a real transaction.")
print("The MCP server at https://mcp.rickycambrian.org/monetized should process this.")
print()
print("To make this work in the agent, we need to:")
print("1. Use the fluora MCP server that's configured")
print("2. Make the request through the proper MCP protocol")
print("3. See the transaction at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
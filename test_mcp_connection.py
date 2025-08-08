#!/usr/bin/env python3

import asyncio
import json
from anthropic import Anthropic
from anthropic.types.beta import BetaToolResultBlockParam

# Using logged-in authentication (should work by default)
client = Anthropic()

async def test_mcp_connection():
    """Test the monetized MCP connection with a simple Solana price request"""
    
    print("Testing monetized MCP connection...")
    
    # Create a request to get SOL price via monetized MCP
    messages = [
        {
            "role": "user",
            "content": "Use the monetized MCP (fluora) to get the current price of SOL (token address: So11111111111111111111111111111111111111112). Make the purchase using USDC_BASE_SEPOLIA payment method."
        }
    ]
    
    try:
        # Send request to Claude
        response = client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            messages=messages,
            max_tokens=4096,
            tools=[
                {
                    "type": "computer_20241022",
                    "name": "fluora",
                    "display_width_px": 1920,
                    "display_height_px": 1080
                }
            ]
        )
        
        print("\nResponse received:")
        print(json.dumps(response.model_dump(), indent=2))
        
        # Check if the response contains tool use
        for content in response.content:
            if hasattr(content, 'type') and content.type == 'tool_use':
                print(f"\nTool used: {content.name}")
                print(f"Tool input: {json.dumps(content.input, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
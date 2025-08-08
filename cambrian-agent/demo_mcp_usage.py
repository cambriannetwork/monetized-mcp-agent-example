#!/usr/bin/env python3
"""
Demonstration of how the agent uses monetized MCP to access Cambrian API
"""

import asyncio
import json
from datetime import datetime

import anyio
from claude_code_sdk import query, ClaudeCodeOptions

async def demonstrate_mcp_usage():
    """Show how the agent accesses Cambrian data via monetized MCP"""
    
    print("=" * 60)
    print("Cambrian Trading Agent - Monetized MCP Demo")
    print("=" * 60)
    print()
    
    # Configuration for Claude with MCP access
    options = ClaudeCodeOptions(
        max_turns=2,
        allowed_tools=[
            "mcp__fluora__make-purchase",
            "mcp__fluora__list-purchasable-items",
            "Write"
        ],
        system_prompt="You are demonstrating monetized MCP usage. Show the available endpoints and make a sample purchase."
    )
    
    # Prompt to demonstrate MCP usage
    prompt = """Demonstrate the monetized MCP integration:

1. First, list the available purchasable items from the fluora MCP server
2. Then make a purchase to get the current SOL price using these exact parameters:
   - itemId: solanapricecurrent
   - params: {"token_address": "So11111111111111111111111111111111111111112"}
   - paymentMethod: USDC_BASE_SEPOLIA
   - itemPrice: 0.001
   - serverWalletAddress: 0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3

3. Save the result to a file: knowledge/demo_results_{timestamp}.json

Show the raw responses from each step."""
    
    print("Executing MCP demonstration...")
    print()
    
    messages = []
    results = []
    
    async for message in query(prompt=prompt.format(timestamp=datetime.now().strftime('%Y%m%d_%H%M%S')), options=options):
        messages.append(message)
        
        if hasattr(message, 'content') and message.content:
            print(f"Claude: {message.content[:500]}...")
            results.append({
                'timestamp': datetime.now().isoformat(),
                'type': 'response',
                'content': message.content
            })
    
    print()
    print("=" * 60)
    print("Demo Summary:")
    print(f"- Total messages: {len(messages)}")
    print(f"- Results captured: {len(results)}")
    print()
    print("This demonstrates how the agent:")
    print("1. Lists available Cambrian API endpoints via MCP")
    print("2. Makes authenticated purchases to access data")
    print("3. Processes and saves the results")
    print("=" * 60)

if __name__ == "__main__":
    print("\nStarting Monetized MCP Demonstration...\n")
    anyio.run(demonstrate_mcp_usage)
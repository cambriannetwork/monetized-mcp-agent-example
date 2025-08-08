#!/usr/bin/env python3
"""Test the improved agent for a few cycles"""

import asyncio
import sys
from cambrian_agent import CambrianMCPAgent


async def test_agent():
    """Run agent for 3 cycles to see improvements"""
    print("Testing improved agent for 3 cycles...")
    print("=" * 60)
    
    agent = CambrianMCPAgent()
    await agent.initialize()
    
    # Run for 3 cycles
    for i in range(3):
        await agent.execute_cycle()
        
        # Short wait between cycles
        if i < 2:
            print(f"\n💤 Waiting 5 seconds before next cycle...")
            await asyncio.sleep(5)
    
    print("\n" + "=" * 60)
    print("Test complete! Check the findings directory for progressive analysis.")
    print(f"Findings saved in: knowledge/research/findings/")


if __name__ == "__main__":
    try:
        asyncio.run(test_agent())
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(0)
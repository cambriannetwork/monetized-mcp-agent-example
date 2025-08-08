#!/usr/bin/env python3
"""Quick test to verify agent starts correctly"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agent.core import CambrianTradingAgent

async def test_startup():
    """Test that agent starts and runs one cycle"""
    print("Testing agent startup...")
    
    agent = CambrianTradingAgent()
    
    # Initialize
    await agent.initialize()
    
    # Run just one cycle
    print("\nRunning one cycle...")
    await agent._execute_cycle()
    
    # Shutdown
    await agent.shutdown()
    
    print("\n✓ Agent startup test passed!")

if __name__ == "__main__":
    # Simple logging setup
    import logging
    logging.basicConfig(level=logging.INFO)
    
    asyncio.run(test_startup())
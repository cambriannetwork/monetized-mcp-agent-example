#!/usr/bin/env python3
"""Test production agent"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.agent.core_production import CambrianTradingAgentProduction


async def test_production():
    print("Testing production agent...")
    
    agent = CambrianTradingAgentProduction()
    
    # Initialize
    await agent.initialize()
    
    # Run one cycle
    print("\nRunning one production cycle...")
    await agent._execute_cycle()
    
    # Check saved files
    import os
    findings_dir = Path("knowledge/research/findings")
    recent_files = sorted(findings_dir.glob("cycle_*"), key=os.path.getmtime)[-3:]
    
    print("\nRecent findings files:")
    for f in recent_files:
        print(f"  - {f.name}")
    
    # Shutdown
    await agent.shutdown()
    
    print("\n✅ Production test complete!")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    
    asyncio.run(test_production())
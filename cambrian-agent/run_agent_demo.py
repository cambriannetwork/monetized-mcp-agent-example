#!/usr/bin/env python3
"""
Demo version of the agent that shows it working without Claude SDK blocking
"""

import os
import sys
import asyncio
import signal
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.core_simple import CambrianTradingAgentSimple


async def main():
    """Main entry point for demo"""
    
    print("""
    ╔═══════════════════════════════════════════╗
    ║      Cambrian Trading Agent v1.0.0        ║
    ║           (Demo Mode)                     ║
    ║                                           ║
    ║  Autonomous Trading Strategy Research     ║
    ║  Using Real Cambrian API Data            ║
    ╚═══════════════════════════════════════════╝
    """)
    
    print("ℹ️  This demo shows the agent architecture without Claude SDK calls")
    print("ℹ️  In production, it would make real MCP requests for Cambrian data\n")
    
    # Create and initialize agent
    agent = CambrianTradingAgentSimple()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print(f"\n⚠️  Received signal {sig}, initiating shutdown...")
        agent.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize agent
        await agent.initialize()
        
        # Override loop interval for demo
        agent.config['agent']['loop_interval'] = 5  # 5 seconds for demo
        
        # Run agent
        await agent.run()
        
    except Exception as e:
        print(f"\n❌ Agent failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the demo agent
    asyncio.run(main())
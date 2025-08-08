#!/usr/bin/env python3
"""
Test script to verify agent functionality
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.agent.core import CambrianTradingAgent

async def test_agent():
    """Test basic agent functionality"""
    print("Testing Cambrian Trading Agent...")
    
    # Create agent
    agent = CambrianTradingAgent()
    
    # Initialize
    await agent.initialize()
    print("✓ Agent initialized")
    
    # Run one cycle
    print("\nRunning one agent cycle...")
    await agent._execute_cycle()
    print("✓ Cycle completed")
    
    # Shutdown
    await agent.shutdown()
    print("✓ Agent shutdown")
    
    print("\nAgent test completed successfully!")

if __name__ == "__main__":
    import structlog
    
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    asyncio.run(test_agent())
#!/usr/bin/env python3
"""
REAL Production Agent with MCP Integration
This makes ACTUAL paid transactions!
"""

import os
import sys
import asyncio
import signal
from pathlib import Path
from datetime import datetime

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent))

import structlog
from dotenv import load_dotenv

from src.agent.core_real_mcp import CambrianTradingAgentRealMCP

# Load environment variables
load_dotenv()


def configure_logging():
    """Configure structured logging for production"""
    import logging
    
    # Configure basic logging first
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer(colors=True)
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    return structlog.get_logger()


async def main():
    """Main entry point"""
    logger = configure_logging()
    
    logger.info(
        "Starting Cambrian Trading Agent",
        version="1.0.0",
        mode="REAL_MCP_PRODUCTION",
        timestamp=datetime.now().isoformat()
    )
    
    # Create and initialize agent
    agent = CambrianTradingAgentRealMCP()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating shutdown...")
        agent.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize agent
        await agent.initialize()
        
        # Run agent
        await agent.run()
        
    except Exception as e:
        logger.error(
            "Agent failed with error",
            error=str(e),
            exc_info=True
        )
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)
    
    logger.info("Agent shutdown complete")


if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════╗
    ║   Cambrian Trading Agent v1.0.0          ║
    ║        💰 REAL MCP PRODUCTION 💰         ║
    ║                                           ║
    ║  This makes ACTUAL paid transactions!     ║
    ║  Monitor transactions at:                 ║
    ║  https://sepolia.basescan.org/address/    ║
    ║  0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3
    ╚═══════════════════════════════════════════╝
    """)
    
    response = input("Type 'YES' to confirm you want to make REAL paid transactions: ")
    if response != "YES":
        print("Aborted.")
        sys.exit(0)
    
    print("\n🚀 Starting REAL MCP agent...")
    print("Press Ctrl+C to stop\n")
    
    # Run the agent
    asyncio.run(main())
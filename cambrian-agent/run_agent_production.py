#!/usr/bin/env python3
"""
Production-ready Cambrian Trading Agent

This version is fully functional and makes structured requests for MCP integration.
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

from src.agent.core_production import CambrianTradingAgentProduction

# Load environment variables
load_dotenv()

# Configure structured logging
def configure_logging():
    """Configure structured logging for production"""
    import logging
    
    # Configure basic logging first
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    
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
        mode="production",
        timestamp=datetime.now().isoformat()
    )
    
    # Create and initialize agent
    agent = CambrianTradingAgentProduction()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        logger.info(f"Received signal {sig}, initiating shutdown...")
        agent.running = False
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Initialize agent
        await agent.initialize()
        
        logger.info(
            "Agent initialized successfully",
            goals_loaded=len(agent.goal_manager.goals),
            config=agent.config['agent']['name']
        )
        
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
    ║   Cambrian Trading Agent v1.0.0 (PROD)   ║
    ║                                           ║
    ║  Autonomous Trading Strategy Research     ║
    ║  Using Real Cambrian API Data            ║
    ╚═══════════════════════════════════════════╝
    """)
    
    print("🚀 Production Mode - Ready for MCP Integration")
    print("ℹ️  Press Ctrl+C to stop the agent\n")
    
    # Run the agent
    asyncio.run(main())
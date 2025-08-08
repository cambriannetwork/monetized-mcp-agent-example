#!/usr/bin/env python3
"""
Core agent implementation using Claude Code SDK
"""

import asyncio
import json
import yaml
import structlog
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import anyio
from claude_code_sdk import query, ClaudeCodeOptions, Message

from ..persistence.state_manager import StateManager
from ..data.cambrian_client import CambrianClient
from .goals import GoalManager
from .orchestrator import Orchestrator
from .research_agent import ResearchAgent

logger = structlog.get_logger()


class CambrianTradingAgent:
    """Main agent class that orchestrates all components"""
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        self.config = self._load_config(config_path)
        self.state_manager = StateManager(self.config)
        self.goal_manager = GoalManager(self.config)
        self.cambrian_client = CambrianClient(self.config)
        self.orchestrator = Orchestrator(self.config)
        self.research_agent = ResearchAgent(self.config)
        self.running = False
        
        # Load MCP config
        mcp_config_path = Path("config/mcp_config.json")
        with open(mcp_config_path) as f:
            self.mcp_config = json.load(f)
    
    def _load_config(self, config_path: str) -> Dict:
        """Load agent configuration"""
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    async def initialize(self):
        """Initialize agent and restore state"""
        logger.info("Initializing Cambrian Trading Agent")
        print("Initializing agent components...")
        
        # Load previous state
        state = await self.state_manager.load_state()
        if state:
            logger.info("Restored previous state", 
                       last_run=state.get('last_run'),
                       goals_count=len(state.get('active_goals', [])))
            print(f"✓ Restored previous state (last run: {state.get('last_run', 'unknown')})")
        else:
            print("✓ Starting fresh (no previous state)")
        
        # Initialize goals
        await self.goal_manager.load_goals()
        print(f"✓ Loaded {len(self.goal_manager.goals)} research goals")
        
        logger.info("Agent initialized successfully")
        print("✓ Agent initialized successfully\n")
    
    async def run(self):
        """Main agent loop"""
        self.running = True
        logger.info("Starting agent main loop")
        
        try:
            while self.running:
                loop_start = datetime.now()
                
                # Execute main agent cycle
                await self._execute_cycle()
                
                # Calculate sleep time
                elapsed = (datetime.now() - loop_start).total_seconds()
                sleep_time = max(0, self.config['agent']['loop_interval'] - elapsed)
                
                if sleep_time > 0:
                    logger.info(f"Sleeping for {sleep_time:.1f} seconds")
                    await asyncio.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error("Agent error", error=str(e), exc_info=True)
        finally:
            await self.shutdown()
    
    async def _execute_cycle(self):
        """Execute one cycle of the agent"""
        logger.info("Starting agent cycle", timestamp=datetime.now().isoformat())
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Executing agent cycle...")
        
        # Get current goals
        active_goals = await self.goal_manager.get_active_goals()
        logger.info(f"Active goals: {len(active_goals)}")
        print(f"Active goals: {len(active_goals)}")
        
        if active_goals:
            print(f"Working on: {active_goals[0].title}")
        
        # Use Claude to analyze and execute next steps
        await self._claude_execute_goals(active_goals)
        
        # Save state
        await self.state_manager.save_state({
            'last_run': datetime.now().isoformat(),
            'active_goals': [g.to_dict() for g in active_goals],
            'cycle_count': self.state_manager.state.get('cycle_count', 0) + 1
        })
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Cycle completed")
    
    async def _claude_execute_goals(self, goals: List):
        """Use Claude to analyze goals and execute next steps"""
        
        # Prepare context for Claude
        goals_context = "\n".join([
            f"- {g.title} (Priority: {g.priority}, Status: {g.status})"
            for g in goals[:3]  # Focus on top 3 goals
        ])
        
        prompt = f"""You are an autonomous trading agent researching Solana trading strategies using the Cambrian API.

Current Goals:
{goals_context}

Available Tools:
- Access to Cambrian API via monetized MCP (fluora server)
- File system access for saving research and findings
- Analysis capabilities

Your task:
1. Review the current goals
2. Use the Cambrian API to gather relevant data (via fluora MCP)
3. Analyze the data and identify insights
4. Save your findings to the appropriate files
5. Update progress on goals

Focus on goal #1 if it's not completed. Use real Cambrian API data only - no mock data.
Remember to save all findings to files in the knowledge/ directory.

What specific research or analysis will you perform this cycle?"""

        # Configure Claude options
        options = ClaudeCodeOptions(
            max_turns=5,
            allowed_tools=[
                "Read", "Write", "Edit",
                "mcp__fluora__make-purchase",
                "mcp__fluora__list-purchasable-items"
            ],
            system_prompt="""You are an autonomous trading research agent. 
Always use real Cambrian API data via the monetized MCP.
Save all findings and progress to files.
Focus on quantifiable metrics and actionable insights."""
        )
        
        try:
            messages = []
            async for message in query(prompt=prompt, options=options):
                messages.append(message)
                
                # Log assistant responses
                if hasattr(message, 'content') and message.content:
                    logger.info("Claude response", content=message.content[:200])
            
            logger.info(f"Claude completed cycle with {len(messages)} messages")
            
        except Exception as e:
            logger.error("Error in Claude execution", error=str(e))
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down agent")
        self.running = False
        
        # Save final state
        await self.state_manager.save_state({
            'last_run': datetime.now().isoformat(),
            'shutdown_time': datetime.now().isoformat(),
            'status': 'stopped'
        })


async def main():
    """Entry point"""
    agent = CambrianTradingAgent()
    await agent.initialize()
    await agent.run()


if __name__ == "__main__":
    # Configure structured logging
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
            structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    anyio.run(main)
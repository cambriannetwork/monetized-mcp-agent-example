#!/usr/bin/env python3
"""
Production agent with real MCP integration
"""

import asyncio
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..persistence.state_manager import StateManager
from ..data.cambrian_client import CambrianClient
from .goals import GoalManager
from .orchestrator import Orchestrator
from ..mcp.fluora_client import FluoraMCPClient

import structlog

logger = structlog.get_logger()


class CambrianTradingAgentMCP:
    """Production agent that makes real MCP requests"""
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        self.config = self._load_config(config_path)
        self.state_manager = StateManager(self.config)
        self.goal_manager = GoalManager(self.config)
        self.cambrian_client = CambrianClient(self.config)
        self.orchestrator = Orchestrator(self.config)
        self.mcp_client = FluoraMCPClient()
        self.running = False
        self.cycle_count = 0
    
    def _load_config(self, config_path: str) -> Dict:
        """Load agent configuration"""
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    async def initialize(self):
        """Initialize agent and restore state"""
        logger.info("Initializing Cambrian Trading Agent (MCP Production)")
        print("Initializing agent with MCP integration...")
        
        # Load previous state
        state = await self.state_manager.load_state()
        if state:
            logger.info("Restored previous state", 
                       last_run=state.get('last_run'),
                       goals_count=len(state.get('active_goals', [])))
            print(f"✓ Restored previous state (cycles completed: {state.get('cycle_count', 0)})")
            self.cycle_count = state.get('cycle_count', 0)
        else:
            print("✓ Starting fresh (no previous state)")
        
        # Initialize goals
        await self.goal_manager.load_goals()
        print(f"✓ Loaded {len(self.goal_manager.goals)} research goals")
        
        # Test MCP connection
        print("\n🔌 Testing MCP connection...")
        items = await self.mcp_client.list_purchasable_items()
        if items:
            print(f"✓ MCP connection working ({len(items.get('items', []))} items available)")
        else:
            print("⚠️  MCP connection test failed - continuing anyway")
        
        logger.info("Agent initialized successfully")
        print("✓ Agent initialized successfully\n")
    
    async def run(self):
        """Main agent loop"""
        self.running = True
        logger.info("Starting agent main loop with MCP")
        print(f"Starting agent main loop (interval: {self.config['agent']['loop_interval']}s)")
        print("💰 Real MCP purchases will be made!\n")
        
        try:
            while self.running:
                loop_start = datetime.now()
                
                # Execute main agent cycle
                await self._execute_cycle()
                
                # Calculate sleep time
                elapsed = (datetime.now() - loop_start).total_seconds()
                sleep_time = max(0, self.config['agent']['loop_interval'] - elapsed)
                
                if sleep_time > 0:
                    print(f"\n💤 Sleeping for {sleep_time:.1f} seconds until next cycle...")
                    await asyncio.sleep(sleep_time)
        
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            print("\n\n⚠️  Received interrupt signal")
        except Exception as e:
            logger.error("Agent error", error=str(e), exc_info=True)
            print(f"\n❌ Agent error: {e}")
        finally:
            await self.shutdown()
    
    async def _execute_cycle(self):
        """Execute one cycle of the agent"""
        self.cycle_count += 1
        logger.info("Starting agent cycle", timestamp=datetime.now().isoformat())
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Cycle #{self.cycle_count}")
        print(f"{'='*60}")
        
        # Get current goals
        active_goals = await self.goal_manager.get_active_goals()
        logger.info(f"Active goals: {len(active_goals)}")
        print(f"\n📋 Active goals: {len(active_goals)}")
        
        for i, goal in enumerate(active_goals[:3], 1):
            print(f"   {i}. {goal.title} ({goal.priority} priority)")
        
        if active_goals:
            current_goal = active_goals[0]
            print(f"\n🔬 Working on: {current_goal.title}")
            
            # Execute research based on goal
            await self._execute_research_for_goal(current_goal)
        
        # Save state
        await self.state_manager.save_state({
            'last_run': datetime.now().isoformat(),
            'active_goals': [g.to_dict() for g in active_goals],
            'cycle_count': self.cycle_count
        })
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Cycle #{self.cycle_count} completed")
    
    async def _execute_research_for_goal(self, goal):
        """Execute research for a specific goal"""
        print(f"\n📊 Executing research for: {goal.title}")
        
        # Determine what data to request based on goal
        if "market analysis" in goal.title.lower():
            await self._research_market_analysis()
        elif "arbitrage" in goal.title.lower():
            await self._research_arbitrage()
        elif "momentum" in goal.title.lower():
            await self._research_momentum()
        else:
            print("ℹ️  General research mode")
            await self._research_general()
    
    async def _research_market_analysis(self):
        """Research market analysis using REAL MCP calls"""
        print("\n📈 Researching market conditions with REAL MCP calls...")
        
        # Get SOL price via MCP
        print("\n💳 Making MCP purchase for SOL price...")
        sol_data = await self.mcp_client.get_token_price(
            "So11111111111111111111111111111111111111112", 
            "SOL"
        )
        
        if sol_data:
            print("✅ SOL price data received!")
            print(f"   Response: {json.dumps(sol_data, indent=2)[:200]}...")
        else:
            print("❌ Failed to get SOL price")
        
        # Get USDC price via MCP
        print("\n💳 Making MCP purchase for USDC price...")
        usdc_data = await self.mcp_client.get_token_price(
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v", 
            "USDC"
        )
        
        if usdc_data:
            print("✅ USDC price data received!")
            print(f"   Response: {json.dumps(usdc_data, indent=2)[:200]}...")
        else:
            print("❌ Failed to get USDC price")
        
        # Save findings with real data
        findings = {
            'timestamp': datetime.now().isoformat(),
            'research_type': 'market_analysis',
            'cycle': self.cycle_count,
            'mcp_purchases_made': True,
            'data': {
                'SOL': {
                    'mcp_response': sol_data,
                    'success': bool(sol_data)
                },
                'USDC': {
                    'mcp_response': usdc_data,
                    'success': bool(usdc_data)
                }
            }
        }
        
        await self._save_findings('market_analysis_mcp', findings)
    
    async def _research_arbitrage(self):
        """Research arbitrage opportunities"""
        print("\n💱 Researching arbitrage opportunities...")
        
        # Would make MCP calls for pool data
        print("📡 Would analyze price differences across DEXs via MCP")
        
        findings = {
            'timestamp': datetime.now().isoformat(),
            'research_type': 'arbitrage',
            'cycle': self.cycle_count,
            'status': 'analyzing_dex_prices'
        }
        
        await self._save_findings('arbitrage', findings)
    
    async def _research_momentum(self):
        """Research momentum patterns"""
        print("\n📊 Researching momentum patterns...")
        
        # Would make MCP calls for trending tokens
        print("📡 Would analyze trending tokens via MCP")
        
        findings = {
            'timestamp': datetime.now().isoformat(),
            'research_type': 'momentum',
            'cycle': self.cycle_count,
            'status': 'analyzing_trends'
        }
        
        await self._save_findings('momentum', findings)
    
    async def _research_general(self):
        """General research"""
        print("\n🔍 Conducting general research...")
        
        findings = {
            'timestamp': datetime.now().isoformat(),
            'research_type': 'general',
            'cycle': self.cycle_count
        }
        
        await self._save_findings('general', findings)
    
    async def _save_findings(self, research_type: str, findings: Dict):
        """Save research findings"""
        filename = f"cycle_{self.cycle_count}_{research_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path(f"knowledge/research/findings/{filename}")
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(findings, f, indent=2)
        
        print(f"\n✅ Saved findings to: {filename}")
        logger.info(f"Saved research findings", type=research_type, file=filename)
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("Shutting down agent")
        print("\n\n🛑 Shutting down agent...")
        self.running = False
        
        # Save final state
        await self.state_manager.save_state({
            'last_run': datetime.now().isoformat(),
            'shutdown_time': datetime.now().isoformat(),
            'status': 'stopped',
            'cycle_count': self.cycle_count
        })
        
        print("✅ Agent shutdown complete")
        print(f"   Total cycles completed: {self.cycle_count}")
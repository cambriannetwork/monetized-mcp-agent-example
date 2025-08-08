#!/usr/bin/env python3
"""
Simplified core agent for demonstration
"""

import asyncio
import json
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from ..persistence.state_manager import StateManager
from ..data.cambrian_client import CambrianClient
from .goals import GoalManager
from .orchestrator import Orchestrator


class CambrianTradingAgentSimple:
    """Simplified agent that demonstrates the system without blocking on Claude SDK"""
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        self.config = self._load_config(config_path)
        self.state_manager = StateManager(self.config)
        self.goal_manager = GoalManager(self.config)
        self.cambrian_client = CambrianClient(self.config)
        self.orchestrator = Orchestrator(self.config)
        self.running = False
        self.cycle_count = 0
    
    def _load_config(self, config_path: str) -> Dict:
        """Load agent configuration"""
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    async def initialize(self):
        """Initialize agent and restore state"""
        print("Initializing agent components...")
        
        # Load previous state
        state = await self.state_manager.load_state()
        if state:
            print(f"✓ Restored previous state (cycles completed: {state.get('cycle_count', 0)})")
            self.cycle_count = state.get('cycle_count', 0)
        else:
            print("✓ Starting fresh (no previous state)")
        
        # Initialize goals
        await self.goal_manager.load_goals()
        print(f"✓ Loaded {len(self.goal_manager.goals)} research goals")
        
        print("✓ Agent initialized successfully\n")
    
    async def run(self):
        """Main agent loop"""
        self.running = True
        print(f"Starting agent main loop (interval: {self.config['agent']['loop_interval']}s)")
        
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
            print("\n\n⚠️  Received interrupt signal")
        except Exception as e:
            print(f"\n❌ Agent error: {e}")
        finally:
            await self.shutdown()
    
    async def _execute_cycle(self):
        """Execute one cycle of the agent"""
        self.cycle_count += 1
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Cycle #{self.cycle_count}")
        print(f"{'='*60}")
        
        # Get current goals
        active_goals = await self.goal_manager.get_active_goals()
        print(f"\n📋 Active goals: {len(active_goals)}")
        
        for i, goal in enumerate(active_goals[:3], 1):
            print(f"   {i}. {goal.title} ({goal.priority} priority)")
        
        # Simulate research activity
        if active_goals:
            current_goal = active_goals[0]
            print(f"\n🔬 Researching: {current_goal.title}")
            
            # Simulate MCP data request
            print(f"\n📡 Would request Cambrian data via monetized MCP:")
            print(f"   - Endpoint: solanapricecurrent")
            print(f"   - Token: SOL (So11111111111111111111111111111111111111112)")
            print(f"   - Cost: 0.001 USDC")
            
            # Simulate finding
            finding = {
                'timestamp': datetime.now().isoformat(),
                'goal': current_goal.title,
                'data_requested': 'SOL price data',
                'status': 'simulated'
            }
            
            # Save simulated finding
            finding_file = Path(f"knowledge/research/findings/cycle_{self.cycle_count}_finding.json")
            finding_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(finding_file, 'w') as f:
                json.dump(finding, f, indent=2)
            
            print(f"\n✅ Saved research finding to: {finding_file.name}")
        
        # Save state
        await self.state_manager.save_state({
            'last_run': datetime.now().isoformat(),
            'active_goals': [g.to_dict() for g in active_goals],
            'cycle_count': self.cycle_count
        })
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Cycle #{self.cycle_count} completed")
    
    async def shutdown(self):
        """Graceful shutdown"""
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
#!/usr/bin/env python3
"""
Production agent that makes REAL MCP calls via subprocess
"""

import asyncio
import json
import yaml
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..persistence.state_manager import StateManager
from ..data.cambrian_client import CambrianClient
from .goals import GoalManager
from .orchestrator import Orchestrator

import structlog

logger = structlog.get_logger()


class CambrianTradingAgentRealMCP:
    """Production agent that makes REAL MCP requests via subprocess"""
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        self.config = self._load_config(config_path)
        self.state_manager = StateManager(self.config)
        self.goal_manager = GoalManager(self.config)
        self.cambrian_client = CambrianClient(self.config)
        self.orchestrator = Orchestrator(self.config)
        self.running = False
        self.cycle_count = 0
        
        # MCP command setup
        self.mcp_command = [
            "/Users/riccardoesclapon/.nvm/versions/node/v22.16.0/bin/node",
            "--experimental-global-webcrypto",
            "/Users/riccardoesclapon/.nvm/versions/node/v22.16.0/bin/fluora-mcp"
        ]
        self.mcp_env = {
            "FLUORA_API_URL": "https://2bwsfmjzdd.us-west-2.awsapprunner.com/api",
            "NODE_OPTIONS": "--experimental-global-webcrypto",
            "FLUORA_MCP_SERVER_URL": "http://localhost:80"
        }
    
    def _load_config(self, config_path: str) -> Dict:
        """Load agent configuration"""
        with open(config_path) as f:
            return yaml.safe_load(f)
    
    async def initialize(self):
        """Initialize agent and restore state"""
        logger.info("Initializing Cambrian Trading Agent (REAL MCP)")
        print("🚀 Initializing agent with REAL MCP integration...")
        print("💰 This will make REAL paid transactions!")
        
        # Load previous state
        state = await self.state_manager.load_state()
        if state:
            self.cycle_count = state.get('cycle_count', 0)
            print(f"✓ Restored previous state (cycles: {self.cycle_count})")
        
        # Initialize goals
        await self.goal_manager.load_goals()
        print(f"✓ Loaded {len(self.goal_manager.goals)} research goals")
        print("✓ Agent initialized successfully\n")
    
    async def run(self):
        """Main agent loop"""
        self.running = True
        print(f"Starting agent (interval: {self.config['agent']['loop_interval']}s)")
        print("🔗 Transactions will appear at:")
        print("   https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3#tokentxns\n")
        
        try:
            while self.running:
                loop_start = datetime.now()
                await self._execute_cycle()
                
                elapsed = (datetime.now() - loop_start).total_seconds()
                sleep_time = max(0, self.config['agent']['loop_interval'] - elapsed)
                
                if sleep_time > 0:
                    print(f"\n💤 Sleeping for {sleep_time:.1f}s...")
                    await asyncio.sleep(sleep_time)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down...")
        finally:
            await self.shutdown()
    
    async def _execute_cycle(self):
        """Execute one cycle"""
        self.cycle_count += 1
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Cycle #{self.cycle_count}")
        print(f"{'='*60}")
        
        active_goals = await self.goal_manager.get_active_goals()
        print(f"\n📋 Active goals: {len(active_goals)}")
        
        if active_goals:
            goal = active_goals[0]
            print(f"🔬 Working on: {goal.title}")
            
            # Make REAL MCP call
            await self._make_real_mcp_purchase()
        
        # Save state
        await self.state_manager.save_state({
            'last_run': datetime.now().isoformat(),
            'cycle_count': self.cycle_count
        })
    
    async def _make_real_mcp_purchase(self):
        """Make a REAL MCP purchase via subprocess"""
        print("\n💳 Making REAL MCP purchase for SOL price...")
        
        # Prepare the request
        mcp_request = {
            "jsonrpc": "2.0",
            "method": "makePurchase",
            "params": {
                "itemId": "solanapricecurrent",
                "params": {
                    "token_address": "So11111111111111111111111111111111111111112"
                },
                "paymentMethod": "USDC_BASE_SEPOLIA",
                "itemPrice": 0.001,
                "serverWalletAddress": "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3"
            },
            "id": self.cycle_count
        }
        
        print(f"📤 Sending MCP request...")
        print(f"   Cost: 0.001 USDC")
        print(f"   Payment: USDC_BASE_SEPOLIA")
        
        try:
            # Run the MCP command
            process = subprocess.Popen(
                self.mcp_command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, **self.mcp_env},
                text=True
            )
            
            # Send request and get response
            stdout, stderr = process.communicate(
                input=json.dumps(mcp_request)
            )
            
            if stderr:
                print(f"⚠️  MCP stderr: {stderr}")
            
            if stdout:
                print(f"📥 MCP response received!")
                try:
                    response = json.loads(stdout)
                    print(f"✅ Response: {json.dumps(response, indent=2)[:300]}...")
                    
                    # Save the response
                    await self._save_mcp_response(response)
                except json.JSONDecodeError:
                    print(f"❌ Invalid JSON response: {stdout[:200]}")
            else:
                print("❌ No response from MCP")
                
        except Exception as e:
            print(f"❌ MCP error: {e}")
            logger.error("MCP call failed", error=str(e))
    
    async def _save_mcp_response(self, response: Dict):
        """Save MCP response"""
        filename = f"mcp_response_{self.cycle_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = Path(f"knowledge/research/mcp_responses/{filename}")
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump({
                'cycle': self.cycle_count,
                'timestamp': datetime.now().isoformat(),
                'response': response
            }, f, indent=2)
        
        print(f"💾 Saved response to: {filename}")
    
    async def shutdown(self):
        """Shutdown"""
        self.running = False
        await self.state_manager.save_state({
            'last_run': datetime.now().isoformat(),
            'cycle_count': self.cycle_count,
            'status': 'stopped'
        })
        print(f"\n✅ Shutdown complete (cycles: {self.cycle_count})")
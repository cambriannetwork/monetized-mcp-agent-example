#!/usr/bin/env python3
"""
FINAL Production Agent - Uses Claude SDK with MCP tools
This is the REAL implementation that makes paid calls
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import anyio
from claude_code_sdk import query, ClaudeCodeOptions

from src.persistence.state_manager import StateManager
from src.agent.goals import GoalManager


class RealMCPAgent:
    """Agent that makes REAL MCP purchases"""
    
    def __init__(self):
        self.state_manager = StateManager({'persistence': {'state_file': 'knowledge/state.json'}})
        self.goal_manager = GoalManager({'agent': {}})
        self.cycle_count = 0
        self.running = False
    
    async def initialize(self):
        """Initialize agent"""
        print("🚀 Initializing REAL MCP Agent...")
        
        state = await self.state_manager.load_state()
        if state:
            self.cycle_count = state.get('cycle_count', 0)
            print(f"✓ Restored state (cycles: {self.cycle_count})")
        
        await self.goal_manager.load_goals()
        print(f"✓ Loaded {len(self.goal_manager.goals)} goals")
        print("✓ Ready to make REAL MCP purchases\n")
    
    async def run_cycle(self):
        """Run one cycle with REAL MCP purchase"""
        self.cycle_count += 1
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Cycle #{self.cycle_count}")
        print(f"{'='*60}")
        
        # Make REAL MCP purchase using Claude SDK
        print("\n💳 Making REAL MCP purchase...")
        
        prompt = f"""Cycle #{self.cycle_count}: Make a REAL monetized MCP purchase.

Use the mcp__fluora__make-purchase tool with these parameters:
- itemId: "solanapricecurrent"  
- params: {{"token_address": "So11111111111111111111111111111111111111112"}}
- paymentMethod: "USDC_BASE_SEPOLIA"
- itemPrice: 0.001
- serverWalletAddress: "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3"

This is a REAL purchase that costs 0.001 USDC. Extract and save the price data."""
        
        options = ClaudeCodeOptions(
            max_turns=2,
            allowed_tools=["mcp__fluora__make-purchase", "Write"],
            system_prompt="Make REAL MCP purchases and save results"
        )
        
        print("📤 Sending MCP request via Claude...")
        
        messages = []
        async for message in query(prompt=prompt, options=options):
            messages.append(message)
            if hasattr(message, 'content') and message.content:
                print(f"\n📥 Response: {message.content[:200]}...")
        
        # Save state
        await self.state_manager.save_state({
            'last_run': datetime.now().isoformat(),
            'cycle_count': self.cycle_count,
            'last_mcp_call': datetime.now().isoformat()
        })
        
        print(f"\n✅ Cycle #{self.cycle_count} complete")
        print("Check transactions at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
    
    async def run(self):
        """Main loop"""
        self.running = True
        
        try:
            while self.running:
                await self.run_cycle()
                
                print(f"\n💤 Waiting 300 seconds...")
                await asyncio.sleep(300)
        
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down...")
            self.running = False


async def main():
    """Main entry point"""
    
    print("""
    ╔═══════════════════════════════════════════╗
    ║     REAL MCP PRODUCTION AGENT v1.0       ║
    ║                                           ║
    ║   💰 Makes ACTUAL paid transactions! 💰   ║
    ║                                           ║
    ║   Each cycle costs 0.001 USDC on         ║
    ║   Base Sepolia testnet                   ║
    ╚═══════════════════════════════════════════╝
    """)
    
    print("⚠️  WARNING: This agent makes REAL paid MCP calls!")
    print("📍 Monitor at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
    print()
    
    response = input("Type 'CONFIRM' to start making real transactions: ")
    if response != "CONFIRM":
        print("Cancelled.")
        return
    
    agent = RealMCPAgent()
    await agent.initialize()
    await agent.run()


if __name__ == "__main__":
    anyio.run(main)
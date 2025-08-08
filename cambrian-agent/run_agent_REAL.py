#!/usr/bin/env python3
"""
REAL Cambrian Trading Agent using MCP
This actually makes paid transactions through the fluora MCP server
"""

import anyio
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from claude_code_sdk import (
    query,
    ClaudeCodeOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock
)

from src.persistence.state_manager import StateManager
from src.agent.goals import GoalManager

# Load environment variables
load_dotenv()


class CambrianMCPAgent:
    """Agent that makes REAL MCP purchases through fluora server"""
    
    def __init__(self):
        config = {'persistence': {'state_file': 'knowledge/state.json'}, 'agent': {}}
        self.state_manager = StateManager(config)
        self.goal_manager = GoalManager(config)
        self.cycle_count = 0
        self.running = False
        
    async def initialize(self):
        """Initialize agent and restore state"""
        print("🚀 Initializing Cambrian MCP Agent...")
        print("💰 This will make REAL purchases through the monetized MCP!")
        
        # Load previous state
        state = await self.state_manager.load_state()
        if state:
            self.cycle_count = state.get('cycle_count', 0)
            print(f"✓ Restored state (cycles completed: {self.cycle_count})")
        else:
            print("✓ Starting fresh")
            
        # Load goals
        await self.goal_manager.load_goals()
        print(f"✓ Loaded {len(self.goal_manager.goals)} research goals")
        print("✓ Agent initialized\n")
    
    async def execute_cycle(self):
        """Execute one research cycle with REAL MCP purchases"""
        self.cycle_count += 1
        
        print(f"\n{'='*60}")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Cycle #{self.cycle_count}")
        print(f"{'='*60}")
        
        # Get active goals
        active_goals = await self.goal_manager.get_active_goals()
        print(f"\n📋 Active goals: {len(active_goals)}")
        
        if active_goals:
            goal = active_goals[0]
            print(f"🔬 Working on: {goal.title}")
            
            # Execute research based on goal type
            if "market analysis" in goal.title.lower():
                await self.research_market_analysis()
            elif "arbitrage" in goal.title.lower():
                await self.research_arbitrage_opportunities()
            else:
                await self.research_general()
        
        # Save state
        await self.state_manager.save_state({
            'last_run': datetime.now().isoformat(),
            'cycle_count': self.cycle_count,
            'active_goals': [g.to_dict() for g in active_goals]
        })
        
        print(f"\n✅ Cycle #{self.cycle_count} completed")
    
    async def research_market_analysis(self):
        """Research market conditions using REAL MCP purchases"""
        
        system_prompt = """You are a Cambrian Trading Agent researching Solana market conditions.
You have access to the fluora MCP server which can purchase real-time data from the Cambrian API.

IMPORTANT: You MUST make REAL purchases using the mcp__fluora__make-purchase tool.
Each purchase costs 0.001 USDC and will appear on the blockchain."""
        
        # Configure options with fluora MCP server
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            mcp_config="../config/mcp_config.json",  # Use the existing config
            allowed_tools=[
                "mcp__fluora__make-purchase",
                "mcp__fluora__list-purchasable-items",
                "Write"  # To save findings
            ],
            max_turns=5,
            verbose=True  # Enable verbose logging to see MCP communication
        )
        
        # Research prompt
        prompt = f"""Cycle #{self.cycle_count}: Research current Solana market conditions.

1. First, use mcp__fluora__list-purchasable-items to see available data endpoints
2. Then make a REAL purchase for SOL price data using mcp__fluora__make-purchase with:
   - itemId: "solanapricecurrent"
   - params: {"token_address": "So11111111111111111111111111111111111111112"}
   - paymentMethod: "USDC_BASE_SEPOLIA"
   - itemPrice: 0.001
   - serverWalletAddress: "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3"

3. Extract the price from the response and save findings to:
   knowledge/research/findings/cycle_{self.cycle_count}_market_analysis.json

This is a REAL purchase that will cost 0.001 USDC on Base Sepolia."""
        
        print("\n📈 Researching market conditions...")
        print("💳 Making REAL MCP purchases...")
        
        # Track messages for debugging
        messages_received = []
        tool_uses = []
        tool_results = []
        
        # Execute the query
        async for message in query(prompt=prompt, options=options):
            messages_received.append(message)
            
            if isinstance(message, AssistantMessage):
                print("\n>>> Claude:")
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"  Text: {block.text[:200]}...")
                    elif isinstance(block, ToolUseBlock):
                        print(f"  🔧 Using tool: {block.name}")
                        print(f"  📤 Input: {json.dumps(block.input, indent=2)}")
                        tool_uses.append({
                            'tool': block.name,
                            'input': block.input,
                            'id': block.id
                        })
                        
            elif isinstance(message, ResultMessage):
                print("\n<<< Tool Result:")
                for block in message.content:
                    if isinstance(block, ToolResultBlock):
                        print(f"  📥 Result for {block.tool_use_id}:")
                        print(f"  {str(block.content)[:300]}...")
                        tool_results.append({
                            'tool_use_id': block.tool_use_id,
                            'content': block.content
                        })
        
        # Log summary
        print(f"\n📊 Research Summary:")
        print(f"  - Messages: {len(messages_received)}")
        print(f"  - Tool uses: {len(tool_uses)}")
        print(f"  - Tool results: {len(tool_results)}")
        
        # Check if MCP purchase was made
        mcp_purchases = [t for t in tool_uses if t['tool'] == 'mcp__fluora__make-purchase']
        if mcp_purchases:
            print(f"\n✅ Made {len(mcp_purchases)} REAL MCP purchase(s)!")
            print("🔗 Check transaction at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
        else:
            print("\n⚠️  No MCP purchases made this cycle")
    
    async def research_arbitrage_opportunities(self):
        """Research arbitrage opportunities across DEXs"""
        print("\n💱 Researching arbitrage opportunities...")
        
        # Similar structure but focused on DEX data
        system_prompt = """You are researching arbitrage opportunities across Solana DEXs.
Use the fluora MCP server to purchase pool and price data from different DEXs."""
        
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            mcp_config="../config/mcp_config.json",
            allowed_tools=[
                "mcp__fluora__make-purchase",
                "Write"
            ],
            max_turns=5
        )
        
        prompt = f"""Research arbitrage opportunities by comparing prices across DEXs.
Make REAL purchases for pool data if available."""
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name == "mcp__fluora__make-purchase":
                        print(f"💳 Making MCP purchase: {block.input.get('itemId', 'unknown')}")
    
    async def research_general(self):
        """General research"""
        print("\n🔍 Conducting general research...")
        # Simplified for brevity
    
    async def run(self):
        """Main agent loop"""
        self.running = True
        
        try:
            while self.running:
                await self.execute_cycle()
                
                # Wait before next cycle
                print(f"\n💤 Waiting 300 seconds until next cycle...")
                await asyncio.sleep(300)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down...")
            self.running = False


async def main():
    """Main entry point"""
    
    print("""
    ╔═══════════════════════════════════════════╗
    ║     Cambrian Trading Agent v2.0          ║
    ║        REAL MCP Implementation            ║
    ║                                           ║
    ║   💰 Makes REAL monetized purchases! 💰   ║
    ║                                           ║
    ║   Using fluora MCP server configured in:  ║
    ║   config/mcp_config.json                  ║
    ╚═══════════════════════════════════════════╝
    """)
    
    print("\n⚠️  WARNING: This agent makes REAL paid MCP calls!")
    print("📍 Each call costs 0.001 USDC on Base Sepolia")
    print("🔗 Monitor at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
    print()
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found")
        print("Please set it in your .env file or environment")
        return
    
    response = input("Type 'START' to begin making REAL transactions: ")
    if response != "START":
        print("Cancelled.")
        return
    
    # Create and run agent
    agent = CambrianMCPAgent()
    await agent.initialize()
    await agent.run()


if __name__ == "__main__":
    anyio.run(main)
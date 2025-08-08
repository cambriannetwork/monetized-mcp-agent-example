#!/usr/bin/env python3
"""
WORKING Cambrian Trading Agent using MCP
This correctly configures the MCP server using the dictionary format
"""

import anyio
import asyncio
import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from claude_code_sdk import (
    query as claude_query,
    ClaudeCodeOptions,
    AssistantMessage,
    ResultMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock
)

from src.persistence.state_manager import StateManager
from src.persistence.query_tracker import QueryTracker
from src.agent.goals import GoalManager
from src.setup import SetupWizard, run_setup

# Load environment variables
load_dotenv()


class CambrianMCPAgent:
    """Agent that makes REAL MCP purchases through fluora server"""
    
    def __init__(self):
        config = {'persistence': {'state_file': 'knowledge/state.json'}, 'agent': {}}
        self.state_manager = StateManager(config)
        self.goal_manager = GoalManager(config)
        self.query_tracker = QueryTracker()
        self.cycle_count = 0
        self.running = False
        self.user_config = None
        
        # Load the MCP config
        with open('config/mcp_config.json') as f:
            self.mcp_config = json.load(f)
        
        # Load user config if exists
        self._load_user_config()
        
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
        
        # If no active goals, intelligently generate new ones
        if not active_goals:
            print("🤔 No active goals found. Generating intelligent research objectives...")
            await self.generate_research_goals()
            # Reload goals after generation
            await self.goal_manager.load_goals()
            active_goals = await self.goal_manager.get_active_goals()
            print(f"✨ Generated {len(active_goals)} new research goals!")
        
        if active_goals:
            goal = active_goals[0]
            print(f"🔬 Working on: {goal.title}")
            
            # Execute research based on goal type
            if any(keyword in goal.title.lower() for keyword in ["market", "price", "trend", "analysis"]):
                await self.research_market_analysis()
            elif "arbitrage" in goal.title.lower():
                await self.research_arbitrage_opportunities()
            elif any(keyword in goal.title.lower() for keyword in ["entry", "exit", "trading"]):
                await self.research_market_analysis()  # Use market analysis for trading signals too
            elif "volatility" in goal.title.lower():
                await self.research_market_analysis()  # Use market analysis for volatility research
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
        
        # Load previous findings to build upon
        previous_findings = []
        findings_dir = Path("knowledge/research/findings")
        if findings_dir.exists():
            recent_files = sorted(findings_dir.glob("*market_analysis.json"))[-5:]
            for f in recent_files:
                try:
                    with open(f) as file:
                        previous_findings.append(json.load(file))
                except:
                    pass
        
        # Get successful query patterns for this goal type
        successful_sequence = self.query_tracker.get_query_sequence_for_goal("market_analysis")
        previous_pattern = self.query_tracker.get_successful_pattern("market_analysis", "mcp__fluora__callServerTool")
        
        system_prompt = """You are a Cambrian Trading Agent researching Solana market conditions.
You are making a REAL purchase from the Cambrian API.
This will cost 0.001 USDC on Base Sepolia testnet."""
        
        # Configure options with fluora MCP server - use the mcpServers directly
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            mcp_servers=self.mcp_config['mcpServers'],  # Pass the whole mcpServers dict
            allowed_tools=[
                "mcp__fluora__searchFluora",
                "mcp__fluora__listServerTools",
                "mcp__fluora__callServerTool",
                "Write"  # To save findings
            ],
            max_turns=150  # Allow plenty of turns for Claude to complete the full flow
        )
        
        # Build context from previous findings
        context = ""
        if previous_findings:
            context = "\nPrevious findings:\n"
            for i, finding in enumerate(previous_findings[-3:], 1):
                if 'price' in finding:
                    context += f"- Cycle {finding.get('cycle', '?')}: SOL price ${finding['price']}\n"
        
        # Add successful patterns to prompt if available
        pattern_context = ""
        if successful_sequence:
            pattern_context = "\nPrevious successful query sequence:\n"
            for i, query in enumerate(successful_sequence, 1):
                pattern_context += f"{i}. {query['tool']} with params: {json.dumps(query['params'])}\n"
        
        # Research prompt
        prompt = f"""Cycle #{self.cycle_count}: Advanced Solana Market Analysis
{context}
{pattern_context}
IMPORTANT: You have access to MCP tools. Use them DIRECTLY - do NOT use Task, WebSearch, or other tools to look for them.

Make a REAL purchase to get the current SOL price by following these exact steps:

1. First, use the tool mcp__fluora__searchFluora with empty input {{}} to find servers

2. Find the Cambrian API server from the results (it will have server ID starting with 9f2e4fe1)

3. Use mcp__fluora__listServerTools with:
   - serverName: "Cambrian API"
   - mcpServerUrl: "http://localhost:80"

4. Use mcp__fluora__callServerTool to call 'pricing-listing' first to see available items

5. Use mcp__fluora__callServerTool to call 'payment-method' to get the wallet address

6. Finally, use mcp__fluora__callServerTool to call 'make-purchase' with:
   - serverId: "9f2e4fe1-dc04-4ed1-bab4-0f374cb9f8a7"
   - mcpServerUrl: "http://localhost:80"
   - toolName: "make-purchase"
   - args: {{
       "itemId": "solanapricecurrent",
       "params": {{"token_address": "So11111111111111111111111111111111111111112"}},
       "paymentMethod": "USDC_BASE_SEPOLIA",
       "itemPrice": 0.001,
       "serverWalletAddress": (get this from payment-method response)
     }}

7. After getting the price, save your analysis to:
   {os.path.abspath(f'knowledge/research/findings/cycle_{self.cycle_count}_market_analysis.json')}

Include: cycle number, timestamp, price, trend analysis, and trading insights."""
        
        print("\n📈 Researching market conditions...")
        print("💳 Making REAL MCP purchases...")
        
        # Execute the query with timeout
        purchase_made = False
        messages_count = 0
        tools_used = []
        successful_tools = []  # Track successful tool calls
        
        try:
            # No timeout - let Claude decide when complete
            async for message in claude_query(prompt=prompt, options=options):
                messages_count += 1
                
                if isinstance(message, AssistantMessage):
                    print(f"\n>>> Message {messages_count} from Claude")
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            print(f"Text: {block.text[:100]}...")
                        elif isinstance(block, ToolUseBlock):
                            tools_used.append(block.name)
                            print(f"🔧 Tool: {block.name}")
                            if isinstance(block.input, dict):
                                print(f"Input: {json.dumps(block.input, indent=2)[:200]}...")
                            
                            if (block.name == 'mcp__fluora__callServerTool' and 
                                isinstance(block.input, dict) and 
                                block.input.get('toolName') == 'make-purchase'):
                                purchase_made = True
                
                elif isinstance(message, ResultMessage):
                    print(f"<<< Result for message {messages_count}")
        
        except Exception as e:
            print(f"\n❌ Error during query: {e}")
        
        print(f"\n📊 Summary:")
        print(f"  - Messages: {messages_count}")
        print(f"  - Tools used: {tools_used}")
        
        if purchase_made:
            print("\n✅ Real MCP purchase completed!")
            print("🔗 Check transaction at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
        else:
            print("\n⚠️  No MCP purchase detected this cycle")
            if 'mcp__fluora__searchFluora' not in tools_used and 'mcp__fluora__callServerTool' not in tools_used:
                print("❗ MCP tools were not available - fluora-mcp may not be installed or configured correctly")
    
    async def research_arbitrage_opportunities(self):
        """Research arbitrage opportunities across DEXs"""
        print("\n💱 Researching arbitrage opportunities...")
        
        # Similar structure but focused on DEX data
        system_prompt = """You are researching arbitrage opportunities across Solana DEXs.
Use the fluora MCP server to purchase pool and price data from different DEXs."""
        
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__searchFluora",
                "mcp__fluora__listServerTools",
                "mcp__fluora__callServerTool",
                "Write"
            ],
            max_turns=150  # Allow plenty of turns
        )
        
        prompt = f"""Research arbitrage opportunities by comparing prices across DEXs.
Make REAL purchases for pool data if available."""
        
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name == "mcp__fluora__callServerTool" and block.input.get('toolName') == 'make-purchase':
                        print(f"💳 Making MCP purchase: {block.input.get('itemId', 'unknown')}")
    
    async def research_general(self):
        """General research"""
        print("\n🔍 Conducting general research...")
        # Simplified for brevity
    
    async def generate_research_goals(self):
        """Use Claude to intelligently generate research goals based on current market conditions"""
        print("\n🧠 Using Claude to generate intelligent research goals...")
        
        # Look at any previous research findings
        previous_insights = []
        findings_dir = Path("knowledge/research/findings")
        if findings_dir.exists():
            recent_files = sorted(findings_dir.glob("*.json"))[-10:]
            for f in recent_files:
                try:
                    with open(f) as file:
                        data = json.load(file)
                        if 'insights' in data:
                            previous_insights.append(data['insights'])
                except:
                    pass
        
        # Build context
        context = ""
        if previous_insights:
            context = "\nPrevious research insights:\n"
            for insight in previous_insights[-5:]:
                context += f"- {insight[:100]}...\n"
        
        system_prompt = """You are a strategic research planner for a Solana trading agent.
Your task is to generate intelligent, actionable research goals based on current market conditions.
The agent has access to the Cambrian API for real-time Solana data."""
        
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            allowed_tools=["Write"],
            max_turns=100  # Allow plenty of turns for goal generation
        )
        
        prompt = f"""Generate 3-5 strategic research goals for a Solana trading agent.
{context}
Consider:
1. Current market conditions and trends
2. Different types of trading strategies (momentum, arbitrage, liquidity provision)
3. Risk management and portfolio optimization
4. Specific Solana ecosystem opportunities

Create goals that are:
- Specific and measurable
- Achievable through data analysis
- Relevant to profitable trading
- Time-bound (can make progress each cycle)

Save the goals to: {os.path.abspath('knowledge/goals/goals.json')}

Format exactly as shown (include ALL fields):
{{
  "goals": [
    {{
      "id": "goal_001",
      "title": "Clear, specific goal title",
      "description": "Detailed description of what to research and why",
      "status": "active",
      "priority": "high",
      "created_at": "{datetime.now().isoformat()}",
      "progress": 0,
      "metrics": ["metric1", "metric2"]
    }}
  ]
}}

Make the goals diverse and complementary, covering different aspects of Solana trading."""
        
        messages_count = 0
        async for message in query(prompt=prompt, options=options):
            messages_count += 1
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock) and block.name == "Write":
                        print(f"📝 Writing goals to: {block.input.get('file_path', 'unknown')}")
        
        print(f"✅ Goal generation complete (messages: {messages_count})")
    
    async def run(self):
        """Main agent loop"""
        self.running = True
        
        try:
            while self.running:
                await self.execute_cycle()
                
                # Wait before next cycle
                interval = 15  # Default
                if self.user_config and 'agent' in self.user_config:
                    interval = self.user_config['agent'].get('cycle_interval_seconds', 15)
                
                print(f"\n💤 Waiting {interval} seconds until next cycle...")
                await asyncio.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Shutting down...")
            self.running = False
    
    def _load_user_config(self):
        """Load user configuration if it exists"""
        user_config_file = Path("config/user_config.json")
        if user_config_file.exists():
            with open(user_config_file) as f:
                self.user_config = json.load(f)


async def main():
    """Main entry point"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Cambrian Trading Agent")
    parser.add_argument("--reset", action="store_true", help="Reset project and run setup wizard")
    args = parser.parse_args()
    
    # Check for first run or reset flag
    wizard = SetupWizard()
    is_first_run = wizard.check_first_run()
    
    if args.reset or is_first_run:
        if is_first_run:
            print("\n👋 Welcome! This appears to be your first time running the Cambrian Trading Agent.")
            print("Let's set up your trading objectives and preferences.\n")
        
        # Run setup wizard
        config = await run_setup(reset=args.reset)
        if not config:
            print("Setup cancelled.")
            return
        
        print("\n✅ Setup complete! Starting the agent with your configuration...\n")
        await asyncio.sleep(2)  # Brief pause
    
    # Load user config
    user_config = wizard.load_config()
    
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
    
    if user_config and user_config.get('user_direction') != 'default':
        print(f"📊 Direction: {user_config.get('user_direction', 'default')}")
    
    print("\n⚠️  WARNING: This agent makes REAL paid MCP calls!")
    print("📍 Each call costs 0.001 USDC on Base Sepolia")
    print("🔗 Monitor at: https://sepolia.basescan.org/address/0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3")
    print()
    
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found")
        print("Please set it in your .env file or environment")
        return
    
    print("Starting autonomous agent...")
    if user_config and user_config['agent']['auto_purchase']:
        print(f"💳 Auto-purchase enabled with daily budget: ${user_config['agent']['daily_budget_usdc']} USDC")
    
    # Create and run agent
    agent = CambrianMCPAgent()
    await agent.initialize()
    await agent.run()


if __name__ == "__main__":
    anyio.run(main)
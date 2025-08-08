#!/usr/bin/env python3
"""
WORKING Cambrian Trading Agent using MCP
This correctly configures the MCP server using the dictionary format
"""

import anyio
import asyncio
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
        
        # Load the MCP config
        with open('config/mcp_config.json') as f:
            self.mcp_config = json.load(f)
        
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
        
        system_prompt = """You are a Cambrian Trading Agent researching Solana market conditions.
You have access to the fluora MCP server which can purchase real-time data from the Cambrian API.

IMPORTANT MCP TOOL USAGE:
- You MUST use mcp__fluora__callServerTool to interact with the Cambrian API
- The serverId is: 9f2e4fe1-dc04-4ed1-bab4-0f374cb9f8a7
- The mcpServerUrl is: https://mcp.rickycambrian.org/monetized
- DO NOT use Task, WebSearch, or other tools to find the API - use the MCP tools directly!

Each purchase costs 0.001 USDC on Base Sepolia testnet.
Analyze trends and patterns in the purchased data to generate actionable trading insights."""
        
        # Configure options with fluora MCP server - use the mcpServers directly
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            mcp_servers=self.mcp_config['mcpServers'],  # Pass the whole mcpServers dict
            allowed_tools=[
                "mcp__fluora__searchFluora",
                "mcp__fluora__callServerTool",
                "mcp__fluora__listServerTools",
                "Write"  # To save findings
            ],
            max_turns=10  # More turns needed for the full purchase flow
        )
        
        # Build context from previous findings
        context = ""
        if previous_findings:
            context = "\nPrevious findings:\n"
            for i, finding in enumerate(previous_findings[-3:], 1):
                if 'price' in finding:
                    context += f"- Cycle {finding.get('cycle', '?')}: SOL price ${finding['price']}\n"
        
        # Research prompt
        prompt = f"""Cycle #{self.cycle_count}: Advanced Solana Market Analysis
{context}
Your task:
1. First, list available tools using mcp__fluora__listServerTools with:
   {{
     "serverId": "9f2e4fe1-dc04-4ed1-bab4-0f374cb9f8a7",
     "mcpServerUrl": "https://mcp.rickycambrian.org/monetized"
   }}

2. Make a REAL purchase for current SOL price using mcp__fluora__callServerTool:
   {{
     "args": {{
       "itemId": "solanapricecurrent",
       "params": {{"token_address": "So11111111111111111111111111111111111111112"}},
       "itemPrice": 0.001,
       "paymentMethod": "USDC_BASE_SEPOLIA",
       "serverWalletAddress": "0x4C3B0B1Cab290300bd5A36AD5f33A607acbD7ac3"
     }},
     "serverId": "9f2e4fe1-dc04-4ed1-bab4-0f374cb9f8a7",
     "toolName": "make-purchase",
     "mcpServerUrl": "https://mcp.rickycambrian.org/monetized"
   }}

3. Analyze the purchased data:
   - Extract current SOL price
   - Calculate price change from previous cycles
   - Identify trends and patterns
   - Generate trading insights

4. Save your complete analysis to:
   {os.path.abspath(f'knowledge/research/findings/cycle_{self.cycle_count}_market_analysis.json')}

Include: cycle number, timestamp, price, change %, trend analysis, and trading insights.

REMEMBER: Use ONLY the mcp__fluora__ tools, NOT Task or WebSearch!"""
        
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
                # ResultMessage doesn't have content attribute
                # Just log that we received a result
                tool_results.append({
                    'type': 'result',
                    'message': str(message)[:100]
                })
        
        # Log summary
        print(f"\n📊 Research Summary:")
        print(f"  - Messages: {len(messages_received)}")
        print(f"  - Tool uses: {len(tool_uses)}")
        print(f"  - Tool results: {len(tool_results)}")
        
        # Check if MCP purchase was made
        mcp_purchases = [t for t in tool_uses if t['tool'] == 'mcp__fluora__callServerTool' and t['input'].get('toolName') == 'make-purchase']
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
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__searchFluora",
                "mcp__fluora__callServerTool",
                "Write"
            ],
            max_turns=10
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
            max_turns=5
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
                print(f"\n💤 Waiting 15 seconds until next cycle...")
                await asyncio.sleep(15)
                
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
    
    print("Starting autonomous agent...")
    print("The agent will make REAL purchases every 15 seconds.")
    
    # Create and run agent
    agent = CambrianMCPAgent()
    await agent.initialize()
    await agent.run()


if __name__ == "__main__":
    anyio.run(main)
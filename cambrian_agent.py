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
import warnings
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from contextlib import redirect_stderr
import io

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
from src.agent.research_engine import ResearchEngine
from src.agent.research_strategies import ResearchStrategies
from src.agent.strategy_research import StrategyResearchEngine, generate_strategy_research_prompt
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
        self.research_engine = ResearchEngine()
        self.strategy_engine = StrategyResearchEngine()
        self.cycle_count = 0
        self.running = False
        self.user_config = None
        self.current_analysis = {}
        self.current_signals = []
        
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
            
            # Strategy research every 5 cycles or on strategy-related goals
            if (self.cycle_count % 5 == 0 or 
                any(keyword in goal.title.lower() for keyword in ["strategy", "profit", "backtest", "trading"])):
                await self.research_strategies()
            # Execute research based on goal type
            elif any(keyword in goal.title.lower() for keyword in ["market", "price", "trend", "analysis"]):
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
        """Intelligent progressive market research"""
        
        print("\n📈 Starting intelligent market research...")
        
        # Get cached MCP details if available
        mcp_cache = self.research_engine.get_mcp_cache()
        
        # Prepare current market state
        current_price = None
        latest_finding = None
        
        # Try to get latest price from recent findings
        findings_dir = Path("knowledge/research/findings")
        if findings_dir.exists():
            recent_files = sorted(findings_dir.glob("cycle_*_market_analysis.json"))
            if recent_files:
                try:
                    with open(recent_files[-1]) as f:
                        latest_finding = json.load(f)
                        current_price = latest_finding.get('price')
                except:
                    pass
        
        # Perform deep analysis if we have data
        if current_price:
            self.current_analysis = self.research_engine.analyze_price_history(current_price, self.cycle_count)
            self.current_signals = self.research_engine.generate_trading_signals(self.current_analysis)
            
            # Display analysis
            print(f"\n📊 Market Analysis:")
            print(f"  Price: ${current_price:.2f}")
            if "trend" in self.current_analysis:
                print(f"  Trend: {self.current_analysis['trend']['direction']} ({self.current_analysis['trend']['strength']:.1f}%)")
            if "volatility_pct" in self.current_analysis:
                print(f"  Volatility: {self.current_analysis['volatility_pct']:.1f}%")
            
            if self.current_signals:
                print(f"\n📍 Trading Signals ({len(self.current_signals)}):")
                for signal in self.current_signals[:3]:
                    print(f"  • {signal['type']}: {signal['action']} - {signal['reason']}")
        
        # Generate intelligent prompt based on cycle and analysis
        prompt = ResearchStrategies.get_progressive_market_analysis_prompt(
            cycle=self.cycle_count,
            analysis=self.current_analysis,
            signals=self.current_signals,
            mcp_cache=mcp_cache
        )
        
        # Advanced system prompt
        system_prompt = """You are an advanced AI trading analyst for the Cambrian Trading Agent.
You make REAL purchases from the Cambrian API (0.001 USDC per call on Base Sepolia).
Your analysis should be progressively more sophisticated with each cycle.
Focus on actionable insights and specific trading setups."""
        
        # Configure options
        options = ClaudeCodeOptions(
            system_prompt=system_prompt,
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__searchFluora",
                "mcp__fluora__listServerTools", 
                "mcp__fluora__callServerTool",
                "Write",
                "Read"  # Allow reading previous findings
            ],
            max_turns=150
        )
        
        print(f"\n🧠 Executing Cycle {self.cycle_count} research strategy...")
        
        # Track execution
        purchase_made = False
        mcp_details_found = False
        messages_count = 0
        tools_used = []
        current_price_found = None
        analysis_saved = False
        
        try:
            # Suppress RuntimeError about cancel scope
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                async for message in claude_query(prompt=prompt, options=options):
                    messages_count += 1
                    
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, TextBlock):
                                # Extract and show key information
                                text = str(block.text)
                                
                                # Look for price in the text
                                if "price" in text.lower() and "$" in text:
                                    import re
                                    price_match = re.search(r'\$(\d+\.?\d*)', text)
                                    if price_match:
                                        current_price_found = float(price_match.group(1))
                                        self._last_price_found = current_price_found  # Track for strategy research
                                        print(f"\n💰 Price found: ${current_price_found:.2f}")
                                        
                                        # SAVE REAL MCP PRICE DATA
                                        if purchase_made:
                                            self.real_data_collector.add_real_mcp_price(
                                                price=current_price_found,
                                                timestamp=datetime.now().isoformat(),
                                                source="MCP_Purchase"
                                            )
                                
                                # Show trading signals
                                if any(keyword in text.lower() for keyword in ['signal', 'setup', 'entry', 'target']):
                                    # Extract just the relevant part
                                    lines = text.split('\n')
                                    for line in lines:
                                        if any(keyword in line.lower() for keyword in ['signal', 'setup', 'entry', 'target', 'stop', 'profit']):
                                            print(f"   📍 {line.strip()}")
                            
                            elif isinstance(block, ToolUseBlock):
                                tools_used.append(block.name)
                                
                                # Track Write operations
                                if block.name == 'Write':
                                    analysis_saved = True
                                    print(f"💾 Saving analysis...")
                                
                                # Track MCP details for caching
                                elif block.name == 'mcp__fluora__callServerTool' and isinstance(block.input, dict):
                                    if block.input.get('toolName') == 'payment-methods':
                                        # Will get wallet address in response
                                        pass
                                    elif block.input.get('toolName') == 'make-purchase':
                                        purchase_made = True
                                        print(f"💳 Making purchase: {block.input.get('args', {}).get('itemId', 'unknown')}")
                                        # Cache the server details
                                        if not mcp_cache and 'serverId' in block.input:
                                            server_id = block.input.get('serverId')
                                            server_url = block.input.get('mcpServerUrl')
                                            wallet = block.input.get('args', {}).get('serverWalletAddress')
                                            if server_id and server_url and wallet:
                                                self.research_engine.save_mcp_cache(server_id, server_url, wallet)
                                                print("✅ Cached MCP connection")
                    
                    # Stop after reasonable messages
                    if messages_count > 20:  # Reduced from 30
                        print(f"\n⚡ Stopping at {messages_count} messages (limit reached)")
                        break
        
        except RuntimeError as e:
            # Ignore cancel scope errors
            if "cancel scope" not in str(e):
                print(f"\n❌ RuntimeError: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
        # Summary
        print(f"\n📊 Cycle {self.cycle_count} Summary:")
        print(f"  Messages: {messages_count}")
        print(f"  Tools used: {len(set(tools_used))}")
        
        if purchase_made:
            print("  ✅ Purchase completed")
            
            # If we found a price, update analysis
            if current_price_found:
                # Update our analysis with the new price
                self.current_analysis = self.research_engine.analyze_price_history(current_price_found, self.cycle_count)
                new_signals = self.research_engine.generate_trading_signals(self.current_analysis)
                
                # Show key metrics
                if "price_change_pct" in self.current_analysis:
                    print(f"  📈 Price change: {self.current_analysis['price_change_pct']:+.2f}%")
                if "trend" in self.current_analysis:
                    trend = self.current_analysis['trend']
                    print(f"  📊 Trend: {trend['direction']} ({trend['consecutive_moves']} moves)")
                if "volatility_pct" in self.current_analysis:
                    print(f"  📉 Volatility: {self.current_analysis['volatility_pct']:.1f}%")
                
                # Show new signals
                if new_signals:
                    print(f"\n  🎯 New Signals Generated:")
                    for signal in new_signals[:2]:
                        print(f"    • {signal['type']}: {signal['action']}")
                
                # Save minimal finding if analysis wasn't saved by Claude
                if not analysis_saved:
                    findings_dir = Path("knowledge/research/findings")
                    findings_dir.mkdir(parents=True, exist_ok=True)
                    
                    finding = {
                        "cycle": self.cycle_count,
                        "timestamp": datetime.now().isoformat(),
                        "price": current_price_found,
                        "analysis": {
                            "trend": self.current_analysis.get("trend"),
                            "volatility": self.current_analysis.get("volatility_pct"),
                            "signals": len(new_signals)
                        }
                    }
                    
                    with open(findings_dir / f"cycle_{self.cycle_count}_market_analysis.json", 'w') as f:
                        json.dump(finding, f, indent=2)
                    print(f"  💾 Saved minimal findings")
            
            # Evolve goals based on findings
            if self.current_signals:
                current_goals = await self.goal_manager.get_active_goals()
                evolved_goals = self.research_engine.evolve_goals(
                    [g.to_dict() for g in current_goals],
                    self.current_analysis,
                    self.current_signals
                )
                
                if len(evolved_goals) > len(current_goals):
                    print(f"  🎯 Generated {len(evolved_goals) - len(current_goals)} new goals")
        else:
            print("  ⚠️  No purchase made this cycle")
    
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
        
        try:
            # Suppress RuntimeError about cancel scope
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                async for message in claude_query(prompt=prompt, options=options):
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, ToolUseBlock) and block.name == "mcp__fluora__callServerTool" and block.input.get('toolName') == 'make-purchase':
                                print(f"💳 Making MCP purchase: {block.input.get('itemId', 'unknown')}")
        except RuntimeError as e:
            # Ignore cancel scope errors
            if "cancel scope" not in str(e):
                print(f"\n❌ RuntimeError: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
    
    async def research_strategies(self):
        """Research and develop profitable trading strategies"""
        print("\n💰 Researching profitable trading strategies...")
        
        # Get current progress
        progress = self.strategy_engine.get_strategy_progress()
        
        # Run strategy research
        report = await self.strategy_engine.research_profitable_strategies(self.cycle_count)
        
        # Show results
        if report['profitable_strategies'] > 0:
            print(f"\n✅ Found {report['profitable_strategies']} profitable strategies!")
            if report['best_strategy']:
                best = report['best_strategy']
                print(f"   Best: {best['name']} - Score: {best['evaluation']['score']}/100")
                print(f"   Expected profit: {best['backtest']['total_pnl_percent']:.1f}%")
        
        # Update data collector with current price if found
        if hasattr(self, '_last_price_found') and self._last_price_found:
            self.strategy_engine.data_collector.add_new_price(self._last_price_found)
        
        # Generate live signals
        if progress['ready_for_deployment'] and hasattr(self, '_last_price_found'):
            signals = self.strategy_engine.get_live_signals(self._last_price_found)
            if signals:
                print(f"\n🎯 Live Trading Signals:")
                for sig in signals:
                    print(f"   • {sig['strategy']}: {sig['signal']['action']} @ ${self._last_price_found:.2f}")
                    print(f"     Stop: ${sig['signal']['stop']:.2f}, Target: ${sig['signal']['target']:.2f}")
    
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
        try:
            # Suppress RuntimeError about cancel scope
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                async for message in claude_query(prompt=prompt, options=options):
                    messages_count += 1
                    if isinstance(message, AssistantMessage):
                        for block in message.content:
                            if isinstance(block, ToolUseBlock) and block.name == "Write":
                                print(f"📝 Writing goals to: {block.input.get('file_path', 'unknown')}")
        except RuntimeError as e:
            # Ignore cancel scope errors
            if "cancel scope" not in str(e):
                print(f"\n❌ RuntimeError: {e}")
        except Exception as e:
            print(f"\n❌ Error: {e}")
        
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
    
    # Suppress specific RuntimeError about cancel scope
    warnings.filterwarnings("ignore", message=".*cancel scope.*different task.*")
    
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
    # Suppress specific RuntimeError warnings
    import logging
    logging.getLogger("anyio").setLevel(logging.ERROR)
    
    # Configure asyncio to suppress task exceptions
    import asyncio
    
    def exception_handler(loop, context):
        # Suppress the specific RuntimeError about cancel scope
        exception = context.get('exception')
        if isinstance(exception, RuntimeError) and 'cancel scope' in str(exception):
            return  # Silently ignore
        # Default handler for other exceptions
        loop.default_exception_handler(context)
    
    # Run with custom exception handler
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.set_exception_handler(exception_handler)
    
    try:
        anyio.run(main)
    finally:
        loop.close()
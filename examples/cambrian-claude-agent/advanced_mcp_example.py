#!/usr/bin/env python3
"""
Advanced MCP Example - Demonstrates various MCP capabilities

This example shows:
1. Service discovery
2. Multiple API calls
3. Data aggregation
4. Error handling
5. Result persistence
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from claude_code_sdk import query, ClaudeCodeOptions, AssistantMessage, ToolUseBlock, TextBlock

# Load environment variables
load_dotenv()


class AdvancedMCPClient:
    """Advanced client for interacting with monetized MCP services"""
    
    def __init__(self):
        # Load MCP configuration
        with open('config/mcp_config.json') as f:
            self.mcp_config = json.load(f)
        
        # Create results directory
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
    
    async def discover_services(self):
        """Discover all available MCP services"""
        print("\n🔍 Discovering available MCP services...")
        
        options = ClaudeCodeOptions(
            system_prompt="You are discovering available MCP services.",
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__exploreServices",
                "mcp__fluora__getServiceDetails"
            ],
            max_turns=5,
            model="claude-sonnet-4-20250514"
        )
        
        prompt = """Please explore all available MCP services:
        1. Use mcp__fluora__exploreServices with category: '' to list all services
        2. For each service found, use mcp__fluora__getServiceDetails to get more information
        3. Summarize what services are available and what they offer"""
        
        services = []
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        if block.name == "mcp__fluora__exploreServices":
                            print(f"  Found services in category: {block.input.get('category', 'all')}")
                    elif isinstance(block, TextBlock):
                        services.append(block.text)
        
        return services
    
    async def get_solana_metrics(self):
        """Get comprehensive Solana metrics"""
        print("\n📊 Fetching Solana metrics...")
        
        options = ClaudeCodeOptions(
            system_prompt="You are gathering Solana market metrics.",
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__exploreServices",
                "mcp__fluora__getServiceDetails",
                "mcp__fluora__callServiceTool"
            ],
            max_turns=10,
            model="claude-sonnet-4-20250514"  
        )
        
        prompt = """Get comprehensive Solana metrics from the Cambrian API:
        1. Find the Cambrian API service
        2. List available pricing items
        3. Get the current SOL price
        4. If available, get 24h volume data
        5. Summarize the market conditions"""
        
        metrics = {}
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, ToolUseBlock):
                        if "make-purchase" in str(block.input):
                            print(f"  💳 Making purchase: {block.input.get('itemId', 'unknown')}")
                            metrics['purchase_made'] = True
                    elif isinstance(block, TextBlock):
                        # Parse any metrics from the response
                        if "price" in block.text.lower():
                            metrics['response'] = block.text
        
        return metrics
    
    async def analyze_arbitrage_opportunities(self):
        """Analyze arbitrage opportunities across DEXs"""
        print("\n💱 Analyzing arbitrage opportunities...")
        
        options = ClaudeCodeOptions(
            system_prompt="You are analyzing arbitrage opportunities across Solana DEXs.",
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__exploreServices",
                "mcp__fluora__callServiceTool",
                "Write"
            ],
            max_turns=10,
            model="claude-sonnet-4-20250514"  
        )
        
        prompt = """Analyze potential arbitrage opportunities:
        1. Use the Cambrian API to check if DEX pool data is available
        2. If available, get price data for major trading pairs
        3. Calculate potential arbitrage opportunities
        4. Save your analysis to results/arbitrage_analysis.json"""
        
        opportunities = []
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and "arbitrage" in block.text.lower():
                        opportunities.append(block.text)
        
        return opportunities
    
    async def monitor_whale_activity(self):
        """Monitor whale wallet activity"""
        print("\n🐋 Monitoring whale activity...")
        
        options = ClaudeCodeOptions(
            system_prompt="You are monitoring large wallet movements on Solana.",
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__exploreServices",
                "mcp__fluora__callServiceTool"
            ],
            max_turns=8,
            model="claude-sonnet-4-20250514"  
        )
        
        prompt = """Check for whale activity data:
        1. Look for any whale tracking or large transaction data in the Cambrian API
        2. If available, get recent large transactions
        3. Identify patterns or significant movements
        4. Provide insights on market impact"""
        
        whale_data = {}
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        whale_data['analysis'] = block.text
        
        return whale_data
    
    async def generate_trading_signals(self):
        """Generate trading signals based on market data"""
        print("\n📈 Generating trading signals...")
        
        # Load recent market data if available
        recent_data = []
        findings_dir = Path("knowledge/research/findings")
        if findings_dir.exists():
            for f in sorted(findings_dir.glob("*.json"))[-5:]:
                try:
                    with open(f) as file:
                        recent_data.append(json.load(file))
                except:
                    pass
        
        options = ClaudeCodeOptions(
            system_prompt="You are a trading signal generator analyzing Solana markets.",
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__callServiceTool",
                "Write"
            ],
            max_turns=8,
            model="claude-sonnet-4-20250514"  
        )
        
        context = "Recent market data:\n"
        for data in recent_data:
            if 'price' in data:
                context += f"- Cycle {data.get('cycle', '?')}: ${data['price']}\n"
        
        prompt = f"""{context}
        
        Generate trading signals:
        1. Get current SOL price from Cambrian API
        2. Analyze trend based on recent data
        3. Generate buy/sell/hold signal with confidence level
        4. Save signals to results/trading_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"""
        
        signals = {}
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and any(word in block.text.lower() for word in ['buy', 'sell', 'hold']):
                        signals['recommendation'] = block.text
        
        return signals
    
    async def save_results(self, results):
        """Save all results to a file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = self.results_dir / f"advanced_analysis_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {filename}")
        return filename
    
    async def run_comprehensive_analysis(self):
        """Run all analysis methods"""
        print("\n" + "="*60)
        print("🚀 Starting Comprehensive MCP Analysis")
        print("="*60)
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'analyses': {}
        }
        
        # Run each analysis
        try:
            # 1. Service Discovery
            services = await self.discover_services()
            results['analyses']['services'] = services
            
            # 2. Solana Metrics
            metrics = await self.get_solana_metrics()
            results['analyses']['metrics'] = metrics
            
            # 3. Arbitrage Analysis
            arbitrage = await self.analyze_arbitrage_opportunities()
            results['analyses']['arbitrage'] = arbitrage
            
            # 4. Whale Monitoring
            whales = await self.monitor_whale_activity()
            results['analyses']['whales'] = whales
            
            # 5. Trading Signals
            signals = await self.generate_trading_signals()
            results['analyses']['signals'] = signals
            
        except Exception as e:
            print(f"\n❌ Error during analysis: {e}")
            results['error'] = str(e)
        
        # Save results
        filename = await self.save_results(results)
        
        print("\n" + "="*60)
        print("✅ Comprehensive Analysis Complete!")
        print("="*60)
        
        return results


async def main():
    """Main function"""
    # Check prerequisites
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Error: ANTHROPIC_API_KEY not found in .env file")
        print("Please set your API key in the .env file")
        return
    
    # Check wallet configuration
    wallet_path = Path.home() / ".fluora" / "wallets.json"
    if not wallet_path.exists():
        print("⚠️  Warning: Wallet not configured at ~/.fluora/wallets.json")
        print("Some features may not work without a funded wallet")
    
    # Create client and run analysis
    client = AdvancedMCPClient()
    
    print("\n🎯 Advanced MCP Example")
    print("This will demonstrate various MCP capabilities")
    print("Some operations may cost USDC if they make purchases\n")
    
    # Ask user what to run
    print("Select an option:")
    print("1. Run comprehensive analysis (all features)")
    print("2. Discover services only")
    print("3. Get Solana metrics")
    print("4. Analyze arbitrage opportunities")
    print("5. Monitor whale activity")
    print("6. Generate trading signals")
    
    choice = input("\nEnter your choice (1-6): ").strip()
    
    if choice == "1":
        await client.run_comprehensive_analysis()
    elif choice == "2":
        services = await client.discover_services()
        print("\nDiscovered services:", services)
    elif choice == "3":
        metrics = await client.get_solana_metrics()
        print("\nSolana metrics:", metrics)
    elif choice == "4":
        arbitrage = await client.analyze_arbitrage_opportunities()
        print("\nArbitrage opportunities:", arbitrage)
    elif choice == "5":
        whales = await client.monitor_whale_activity()
        print("\nWhale activity:", whales)
    elif choice == "6":
        signals = await client.generate_trading_signals()
        print("\nTrading signals:", signals)
    else:
        print("Invalid choice. Please run again and select 1-6.")


if __name__ == "__main__":
    asyncio.run(main())
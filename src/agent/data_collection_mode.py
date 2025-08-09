"""
Data Collection Mode - Efficiently collect real MCP price data
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import json

from claude_code_sdk import (
    query as claude_query,
    ClaudeCodeOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock
)


class DataCollectionMode:
    """Focused mode for collecting real MCP price data efficiently"""
    
    def __init__(self, mcp_config: Dict):
        self.mcp_config = mcp_config
        self.collection_stats = {
            "total_purchases": 0,
            "successful_prices": 0,
            "failed_attempts": 0,
            "total_cost_usdc": 0.0
        }
    
    async def collect_price_batch(self, num_prices: int = 10) -> List[Dict]:
        """Collect a batch of real prices efficiently"""
        print(f"\n📊 Starting batch collection of {num_prices} real price points...")
        
        collected_prices = []
        
        # Optimized prompt for data collection
        prompt = f"""Collect {num_prices} real-time Solana price data points efficiently.

IMPORTANT: Focus ONLY on price collection. For each data point:
1. Call mcp__fluora__searchFluora to find Cambrian
2. Call pricing-listing to get available data
3. Call make-purchase for 'solanapricecurrent' 
4. Extract and save the exact price value
5. Wait 5-10 seconds between purchases to get different timestamps

Be efficient - minimize unnecessary tool calls. 
Extract the EXACT price from each response.
Continue until you have {num_prices} valid price points.

Start now."""

        options = ClaudeCodeOptions(
            system_prompt="You are a data collection agent. Focus solely on efficiently purchasing and extracting Solana price data from the Cambrian MCP server. Be precise with price extraction.",
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__searchFluora",
                "mcp__fluora__listServerTools", 
                "mcp__fluora__callServerTool",
                "Write"
            ],
            max_turns=150
        )
        
        prices_found = 0
        
        try:
            async for message in claude_query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            text = str(block.text)
                            
                            # Enhanced price extraction
                            if "price" in text.lower():
                                import re
                                # Look for various price formats
                                patterns = [
                                    r'price[:\s]+\$?([\d,]+\.?\d*)',
                                    r'\$?([\d,]+\.?\d*)\s*(?:USD|USDC)?',
                                    r'current[:\s]+\$?([\d,]+\.?\d*)',
                                    r'SOL[:\s]+\$?([\d,]+\.?\d*)'
                                ]
                                
                                for pattern in patterns:
                                    matches = re.findall(pattern, text, re.IGNORECASE)
                                    for match in matches:
                                        try:
                                            price = float(match.replace(',', ''))
                                            if 50 < price < 500:  # Reasonable SOL price range
                                                collected_prices.append({
                                                    "price": price,
                                                    "timestamp": datetime.now().isoformat(),
                                                    "source": "MCP_Batch_Collection"
                                                })
                                                prices_found += 1
                                                print(f"✅ Collected price #{prices_found}: ${price:.2f}")
                                                break
                                        except:
                                            pass
                        
                        elif isinstance(block, ToolUseBlock):
                            if block.name == 'mcp__fluora__callServerTool':
                                if isinstance(block.input, dict):
                                    tool_name = block.input.get('toolName', '')
                                    if tool_name == 'make-purchase':
                                        self.collection_stats["total_purchases"] += 1
                                        self.collection_stats["total_cost_usdc"] += 0.001
                                        print(f"💳 Purchase #{self.collection_stats['total_purchases']} made")
                
                # Stop if we have enough prices
                if prices_found >= num_prices:
                    print(f"\n✅ Successfully collected {prices_found} prices!")
                    break
                    
        except Exception as e:
            print(f"\n❌ Error during collection: {e}")
        
        self.collection_stats["successful_prices"] = len(collected_prices)
        
        # Save collection stats
        self._save_stats()
        
        return collected_prices
    
    async def collect_historical_data(self, hours_back: int = 24) -> List[Dict]:
        """Attempt to collect historical price data"""
        print(f"\n📈 Attempting to collect {hours_back} hours of historical data...")
        
        prompt = f"""Search for and purchase historical Solana price data from Cambrian.

Look for data products that include:
- Historical price data
- 24h price history
- Price charts or time series data
- Trading statistics with historical prices

Focus on getting as much historical price data as possible in a single purchase.
Extract ALL price points with their timestamps."""

        options = ClaudeCodeOptions(
            system_prompt="You are collecting historical price data. Look for bulk historical data products.",
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__searchFluora",
                "mcp__fluora__listServerTools", 
                "mcp__fluora__callServerTool",
                "Write"
            ],
            max_turns=100
        )
        
        historical_prices = []
        
        try:
            async for message in claude_query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Look for historical data in responses
                            text = str(block.text)
                            if any(keyword in text.lower() for keyword in ['history', 'historical', '24h', 'chart']):
                                print(f"📊 Found potential historical data...")
                                # Extract any price/time pairs
                                
        except Exception as e:
            print(f"\n❌ Error collecting historical data: {e}")
        
        return historical_prices
    
    def _save_stats(self):
        """Save collection statistics"""
        stats_file = Path("knowledge/real_mcp_data/collection_stats.json")
        stats_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(stats_file, 'w') as f:
            json.dump(self.collection_stats, f, indent=2)
    
    def print_summary(self):
        """Print collection summary"""
        print("\n" + "="*60)
        print("📊 DATA COLLECTION SUMMARY")
        print("="*60)
        print(f"Total MCP Purchases: {self.collection_stats['total_purchases']}")
        print(f"Successful Price Points: {self.collection_stats['successful_prices']}")
        print(f"Failed Attempts: {self.collection_stats['failed_attempts']}")
        print(f"Total Cost: ${self.collection_stats['total_cost_usdc']:.3f} USDC")
        print(f"Cost per Price: ${self.collection_stats['total_cost_usdc'] / max(1, self.collection_stats['successful_prices']):.3f} USDC")
        print("="*60)


async def run_intensive_collection(mcp_config: Dict, target_points: int = 100):
    """Run intensive data collection to quickly build up real data"""
    collector = DataCollectionMode(mcp_config)
    
    print(f"\n🚀 INTENSIVE DATA COLLECTION MODE")
    print(f"Target: {target_points} real price points")
    print(f"Estimated cost: ${target_points * 0.001:.3f} USDC")
    print("-" * 60)
    
    all_prices = []
    
    # First try to get historical data
    historical = await collector.collect_historical_data()
    if historical:
        all_prices.extend(historical)
        print(f"✅ Collected {len(historical)} historical prices")
    
    # Then collect in batches
    batch_size = 20
    while len(all_prices) < target_points:
        remaining = target_points - len(all_prices)
        batch = min(batch_size, remaining)
        
        print(f"\n📦 Collecting batch of {batch} prices...")
        new_prices = await collector.collect_price_batch(batch)
        all_prices.extend(new_prices)
        
        print(f"Progress: {len(all_prices)}/{target_points} prices collected")
        
        # Small delay between batches
        if len(all_prices) < target_points:
            await asyncio.sleep(5)
    
    collector.print_summary()
    
    return all_prices
#!/usr/bin/env python3
"""
Programmatic MCP Data Collector using Claude SDK
Directly calls MCP through Claude to efficiently collect price data
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from claude_code_sdk import (
    query as claude_query,
    ClaudeCodeOptions,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ToolResultBlock
)

from src.strategy.real_mcp_collector import RealMCPDataCollector


class ProgrammaticMCPCollector:
    """Uses Claude programmatically to collect MCP data efficiently"""
    
    def __init__(self):
        self.real_data_collector = RealMCPDataCollector()
        self.prices_collected = 0
        self.total_cost = 0.0
        self.mcp_config = self._load_mcp_config()
        
    def _load_mcp_config(self) -> Dict:
        """Load MCP configuration"""
        with open('config/mcp_config.json') as f:
            return json.load(f)
    
    async def collect_single_price(self) -> Optional[float]:
        """Collect a single price point efficiently"""
        
        prompt = """Execute these steps precisely:
1. Call mcp__fluora__searchFluora with query "cambrian"
2. Call pricing-listing to see available data
3. Call make-purchase for itemId "solanapricecurrent"
4. Extract and return ONLY the price number from the response

Be extremely efficient. Return ONLY the price value."""

        options = ClaudeCodeOptions(
            system_prompt="You are a data collection bot. Execute MCP calls efficiently and return only the requested data.",
            mcp_servers=self.mcp_config['mcpServers'],
            allowed_tools=[
                "mcp__fluora__searchFluora",
                "mcp__fluora__listServerTools", 
                "mcp__fluora__callServerTool"
            ],
            max_turns=10  # Limit turns for efficiency
        )
        
        price = None
        
        try:
            async for message in claude_query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            # Extract price from text
                            text = str(block.text)
                            price_match = re.search(r'(\d+\.?\d*)', text)
                            if price_match:
                                try:
                                    extracted_price = float(price_match.group(1))
                                    if 50 < extracted_price < 500:  # Valid SOL range
                                        price = extracted_price
                                        break
                                except:
                                    pass
                        
                        elif isinstance(block, ToolUseBlock):
                            if block.name == 'mcp__fluora__callServerTool':
                                if block.input.get('toolName') == 'make-purchase':
                                    self.total_cost += 0.001
                
                if price:
                    break
                    
        except Exception as e:
            print(f"Error: {e}")
        
        return price
    
    async def collect_batch(self, batch_size: int = 10) -> List[float]:
        """Collect a batch of prices"""
        prices = []
        
        print(f"\n📦 Collecting batch of {batch_size} prices...")
        
        for i in range(batch_size):
            print(f"  [{i+1}/{batch_size}] Collecting...", end='', flush=True)
            
            price = await self.collect_single_price()
            
            if price:
                # Save immediately
                self.real_data_collector.add_real_mcp_price(
                    price=price,
                    timestamp=datetime.now().isoformat(),
                    source="Programmatic_MCP"
                )
                prices.append(price)
                self.prices_collected += 1
                print(f" ✅ ${price:.2f}")
            else:
                print(" ❌ Failed")
            
            # Small delay between requests
            if i < batch_size - 1:
                await asyncio.sleep(1)
        
        return prices
    
    async def collect_to_target(self, target: int = 100):
        """Collect data until we reach target number of points"""
        
        # Check current status
        try:
            current_prices, _ = self.real_data_collector.get_real_prices()
            current_count = len(current_prices)
        except:
            current_count = 0
        
        needed = max(0, target - current_count)
        
        print(f"\n📊 Data Collection Status")
        print(f"   Current: {current_count} points")
        print(f"   Target: {target} points")
        print(f"   Need: {needed} more points")
        print(f"   Est. cost: ${needed * 0.001:.3f} USDC")
        
        if needed == 0:
            print("\n✅ Already have enough data!")
            return
        
        print("\n🚀 Starting collection...")
        print("-" * 50)
        
        # Collect in batches
        batch_size = 10
        batches_needed = (needed + batch_size - 1) // batch_size
        
        for batch_num in range(batches_needed):
            remaining = needed - (batch_num * batch_size)
            current_batch_size = min(batch_size, remaining)
            
            print(f"\nBatch {batch_num + 1}/{batches_needed}")
            await self.collect_batch(current_batch_size)
            
            # Show progress
            try:
                total_prices, _ = self.real_data_collector.get_real_prices()
                print(f"📈 Total progress: {len(total_prices)}/{target}")
            except:
                pass
        
        self.print_summary()
    
    def print_summary(self):
        """Print collection summary"""
        print("\n" + "="*60)
        print("📊 COLLECTION COMPLETE")
        print("="*60)
        print(f"Prices collected: {self.prices_collected}")
        print(f"Total cost: ${self.total_cost:.3f} USDC")
        
        try:
            total_prices, _ = self.real_data_collector.get_real_prices()
            print(f"Total data points: {len(total_prices)}")
            
            if len(total_prices) >= 100:
                print("\n🎉 SUCCESS! You now have enough data for strategy development!")
            else:
                print(f"\n📍 Still need {100 - len(total_prices)} more points")
        except Exception as e:
            print(f"Error checking total: {e}")
        
        print("="*60)


async def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("🤖 PROGRAMMATIC MCP DATA COLLECTOR")
    print("="*60)
    print("This tool uses Claude programmatically to collect real price data")
    print("More efficient than the standard agent mode")
    print("="*60)
    
    collector = ProgrammaticMCPCollector()
    
    # Ask for confirmation
    response = input("\nCollect data to reach 100 points? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Collection cancelled")
        return
    
    try:
        await collector.collect_to_target(100)
    except KeyboardInterrupt:
        print("\n\n⚠️ Collection interrupted")
        collector.print_summary()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
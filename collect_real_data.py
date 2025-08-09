#!/usr/bin/env python3
"""
Run intensive data collection to quickly gather real MCP price data
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

from src.agent.data_collection_mode import run_intensive_collection
from src.strategy.real_mcp_collector import RealMCPDataCollector


async def main():
    """Run data collection"""
    
    print("\n" + "="*60)
    print("🚀 REAL MCP DATA COLLECTION TOOL")
    print("="*60)
    print("\nThis will make REAL MCP purchases to collect price data!")
    print("Each price point costs 0.001 USDC")
    
    # Load MCP config
    with open('config/mcp_config.json') as f:
        mcp_config = json.load(f)
    
    # Check current data status
    collector = RealMCPDataCollector()
    try:
        current_prices, _ = collector.get_real_prices()
        current_count = len(current_prices)
    except:
        current_count = 0
    
    print(f"\n📊 Current real data points: {current_count}")
    print(f"📍 Need 100 points for strategy development")
    
    if current_count >= 100:
        print("\n✅ You already have enough data for strategy development!")
        return
    
    needed = 100 - current_count
    print(f"\n💡 Need to collect {needed} more price points")
    print(f"💰 Estimated cost: ${needed * 0.001:.3f} USDC")
    
    # Ask for confirmation
    response = input("\nProceed with data collection? (yes/no): ").strip().lower()
    if response != 'yes':
        print("❌ Collection cancelled")
        return
    
    print("\n🔄 Starting intensive data collection...")
    
    # Run collection
    try:
        new_prices = await run_intensive_collection(mcp_config, target_points=needed)
        
        # Save to real data collector
        for price_data in new_prices:
            collector.add_real_mcp_price(
                price=price_data['price'],
                timestamp=price_data['timestamp'],
                source=price_data['source']
            )
        
        print(f"\n✅ Collection complete! Added {len(new_prices)} new price points")
        
        # Show final status
        final_prices, _ = collector.get_real_prices()
        print(f"📊 Total real data points: {len(final_prices)}")
        
        if len(final_prices) >= 100:
            print("\n🎉 SUCCESS! You now have enough data for strategy development!")
        else:
            print(f"\n⚠️  Still need {100 - len(final_prices)} more points")
            
    except Exception as e:
        print(f"\n❌ Collection failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
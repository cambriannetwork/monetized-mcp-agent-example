#!/usr/bin/env python3
"""View the progression of analysis over cycles"""

import json
from pathlib import Path
from datetime import datetime


def view_progress():
    """Display analysis progression"""
    findings_dir = Path("knowledge/research/findings")
    
    if not findings_dir.exists():
        print("No findings yet. Run the agent first.")
        return
    
    files = sorted(findings_dir.glob("cycle_*_market_analysis.json"))
    
    if not files:
        print("No analysis files found.")
        return
    
    print("📊 ANALYSIS PROGRESSION")
    print("=" * 80)
    
    prices = []
    
    for f in files:
        try:
            with open(f) as file:
                data = json.load(file)
                
                cycle = data.get('cycle', '?')
                timestamp = data.get('timestamp', '')
                price = data.get('price', 0)
                
                print(f"\n🔄 Cycle {cycle}")
                print(f"   Time: {timestamp[:19]}")
                print(f"   Price: ${price:.2f}")
                
                prices.append(price)
                
                # Show analysis depth
                if 'analysis' in data:
                    analysis = data['analysis']
                    if 'trend' in analysis:
                        print(f"   Trend: {analysis['trend']}")
                    if 'volatility' in analysis:
                        print(f"   Volatility: {analysis['volatility']}")
                    if 'signals' in analysis:
                        print(f"   Signals: {len(analysis['signals'])} generated")
                
                # Show insights
                if 'insights' in data:
                    print(f"   Insights: {data['insights'][:100]}...")
                
                # Show trading setups
                if 'trading_setups' in data:
                    setups = data['trading_setups']
                    if setups:
                        print(f"   Trading Setups: {len(setups)}")
                        for setup in setups[:2]:
                            if isinstance(setup, dict):
                                print(f"     - {setup.get('type', 'Unknown')}: {setup.get('action', 'Unknown')}")
        
        except Exception as e:
            print(f"Error reading {f}: {e}")
    
    # Show price progression
    if len(prices) >= 2:
        print("\n📈 PRICE PROGRESSION")
        print("=" * 80)
        
        for i, price in enumerate(prices):
            if i == 0:
                print(f"Cycle 1: ${price:.2f} (baseline)")
            else:
                change = price - prices[i-1]
                change_pct = (change / prices[i-1]) * 100
                arrow = "↑" if change > 0 else "↓" if change < 0 else "→"
                print(f"Cycle {i+1}: ${price:.2f} ({arrow} {change_pct:+.2f}%)")
        
        # Overall change
        if len(prices) > 2:
            total_change = prices[-1] - prices[0]
            total_pct = (total_change / prices[0]) * 100
            print(f"\nTotal Change: {total_pct:+.2f}% over {len(prices)} cycles")
    
    # Check for MCP cache
    cache_file = Path("knowledge/mcp_cache.json")
    if cache_file.exists():
        print("\n✅ MCP connection cached - agent is learning!")
    
    # Check for evolved goals
    goals_file = Path("knowledge/goals/goals.json") 
    if goals_file.exists():
        with open(goals_file) as f:
            goals_data = json.load(f)
            goals = goals_data.get('goals', [])
            print(f"\n🎯 Active Goals: {len(goals)}")
            for goal in goals[:3]:
                print(f"  - {goal.get('title', 'Unknown')}")


if __name__ == "__main__":
    view_progress()
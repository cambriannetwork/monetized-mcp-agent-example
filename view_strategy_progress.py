#!/usr/bin/env python3
"""View strategy development progress"""

import json
from pathlib import Path
from datetime import datetime


def view_strategy_progress():
    """Display strategy development progress"""
    
    # Check strategy history
    history_file = Path("knowledge/strategies/strategy_history.json")
    if history_file.exists():
        with open(history_file) as f:
            strategies = json.load(f)
        
        print("📊 STRATEGY DEVELOPMENT PROGRESS")
        print("=" * 80)
        print(f"Total strategies tested: {len(strategies)}")
        
        # Filter by score
        profitable = [s for s in strategies if s["evaluation"]["score"] >= 60]
        excellent = [s for s in strategies if s["evaluation"]["score"] >= 80]
        
        print(f"Profitable strategies (60+ score): {len(profitable)}")
        print(f"Excellent strategies (80+ score): {len(excellent)}")
        
        if strategies:
            print("\n📈 TOP STRATEGIES:")
            print("-" * 80)
            
            # Sort by score
            sorted_strategies = sorted(strategies, 
                                     key=lambda x: x["evaluation"]["score"], 
                                     reverse=True)[:5]
            
            for i, strategy in enumerate(sorted_strategies, 1):
                print(f"\n{i}. {strategy['name']}")
                print(f"   Type: {strategy['type']}")
                print(f"   Score: {strategy['evaluation']['score']}/100")
                print(f"   Win Rate: {strategy['backtest']['win_rate']:.1f}%")
                print(f"   Profit: {strategy['backtest']['total_pnl_percent']:.1f}%")
                print(f"   Sharpe: {strategy['backtest']['sharpe_ratio']:.2f}")
                print(f"   Max DD: {strategy['backtest']['max_drawdown']:.1f}%")
                print(f"   {strategy['evaluation']['recommendation']}")
    else:
        print("No strategy history found yet.")
    
    # Check best strategy
    best_file = Path("knowledge/strategy_research/best_strategy.json")
    if best_file.exists():
        with open(best_file) as f:
            best = json.load(f)
        
        print("\n🏆 CURRENT BEST STRATEGY")
        print("=" * 80)
        print(f"Name: {best['name']}")
        print(f"Score: {best['evaluation']['score']}/100")
        print(f"Expected Return: {best['backtest']['total_pnl_percent']:.1f}%")
        print(f"Status: {best['evaluation']['recommendation']}")
    
    # Check recent research
    research_dir = Path("knowledge/strategy_research")
    if research_dir.exists():
        research_files = sorted(research_dir.glob("cycle_*_strategy_research.json"))
        
        if research_files:
            print("\n🔬 RECENT STRATEGY RESEARCH")
            print("=" * 80)
            
            # Get last 3 research cycles
            for f in research_files[-3:]:
                with open(f) as file:
                    research = json.load(file)
                
                print(f"\nCycle {research['cycle']}:")
                print(f"  Strategies tested: {research['strategies_tested']}")
                print(f"  Profitable found: {research['profitable_strategies']}")
                
                if research.get('recommendations'):
                    print("  Recommendations:")
                    for rec in research['recommendations'][:2]:
                        print(f"    - {rec}")
    
    # Check price cache for data availability
    cache_file = Path("knowledge/market_data/price_cache.json")
    if cache_file.exists():
        with open(cache_file) as f:
            cache = json.load(f)
        
        print(f"\n📊 Market Data: {len(cache.get('prices', []))} price points cached")


if __name__ == "__main__":
    view_strategy_progress()
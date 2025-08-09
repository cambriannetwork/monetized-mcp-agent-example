"""
Strategy Research Module - Integrates strategy development into agent workflow
"""

import json
import asyncio
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
import numpy as np

from ..strategy.mcp_data_collector import MCPDataCollector, MCPStrategyDataProvider
from ..strategy.strategy_developer import StrategyDeveloper
from ..strategy.backtester import evaluate_strategy_profitability


class StrategyResearchEngine:
    """Researches and develops profitable trading strategies"""
    
    def __init__(self):
        self.data_collector = MCPDataCollector()
        self.strategy_developer = StrategyDeveloper()
        self.research_dir = Path("knowledge/strategy_research")
        self.research_dir.mkdir(parents=True, exist_ok=True)
        self.current_best_strategy = None
        self._load_best_strategy()
    
    def _load_best_strategy(self):
        """Load the current best strategy"""
        best_file = self.research_dir / "best_strategy.json"
        if best_file.exists():
            with open(best_file) as f:
                self.current_best_strategy = json.load(f)
    
    def _save_best_strategy(self, strategy: Dict):
        """Save the best strategy"""
        best_file = self.research_dir / "best_strategy.json"
        # Convert numpy types to Python native types
        serializable_strategy = self._convert_numpy_types(strategy)
        with open(best_file, 'w') as f:
            json.dump(serializable_strategy, f, indent=2)
        self.current_best_strategy = serializable_strategy
    
    async def research_profitable_strategies(self, cycle: int) -> Dict:
        """
        Main research function that develops and tests strategies
        
        Returns:
            Research report with strategy recommendations
        """
        print(f"\n🔬 Strategy Research Cycle {cycle}")
        
        # Collect data
        provider = MCPStrategyDataProvider()
        try:
            market_data = await provider.get_strategy_development_data()
            
            prices = market_data["prices"]
            timestamps = market_data["timestamps"]
            
            print(f"  📊 Analyzing {len(prices)} REAL price points")
            print(f"  📈 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
            print(f"  📉 Volatility: {market_data['metrics']['volatility']:.1%}")
        except ValueError as e:
            print(f"\n  ⚠️  {e}")
            print(f"  ❌ Cannot run strategies without sufficient REAL data!")
            print(f"  💡 The agent needs to collect more MCP price data first.")
            return {
                "cycle": cycle,
                "timestamp": datetime.now().isoformat(),
                "error": str(e),
                "data_points": 0,
                "strategies_tested": 0,
                "profitable_strategies": 0,
                "best_strategy": None,
                "market_conditions": {},
                "recommendations": ["Collect more real MCP data before strategy development"]
            }
        
        # Develop strategies
        strategies = self.strategy_developer.develop_strategies(prices, timestamps)
        print(f"\n  🎯 Developed {len(strategies)} strategies")
        
        # Test strategies
        results = self.strategy_developer.test_strategies(strategies, prices, timestamps)
        
        # Analyze results
        profitable_count = 0
        best_strategy = None
        best_score = 0
        
        print("\n  📊 Strategy Backtest Results:")
        for result in results:
            is_profitable = result["evaluation"]["is_profitable"]
            score = result["evaluation"]["score"]
            
            if is_profitable:
                profitable_count += 1
            
            if score > best_score:
                best_score = score
                best_strategy = result
            
            print(f"    • {result['name']}:")
            print(f"      - Win Rate: {result['backtest']['win_rate']:.1f}%")
            print(f"      - Profit: {result['backtest']['total_pnl_percent']:.1f}%")
            print(f"      - Score: {score:.0f}/100")
            print(f"      - {result['evaluation']['recommendation']}")
        
        # Update best strategy if we found a better one
        if best_strategy and (not self.current_best_strategy or 
                            best_strategy["evaluation"]["score"] > 
                            self.current_best_strategy.get("evaluation", {}).get("score", 0)):
            self._save_best_strategy(best_strategy)
            print(f"\n  🏆 New best strategy: {best_strategy['name']}")
        
        # Generate research report
        report = {
            "cycle": cycle,
            "timestamp": datetime.now().isoformat(),
            "data_points": len(prices),
            "strategies_tested": len(results),
            "profitable_strategies": profitable_count,
            "best_strategy": best_strategy,
            "market_conditions": market_data["metrics"],
            "recommendations": self._generate_recommendations(results, market_data)
        }
        
        # Save research
        self._save_research(cycle, report)
        
        return report
    
    def _generate_recommendations(self, results: List[Dict], market_data: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        # Market condition recommendations
        volatility = market_data["metrics"]["volatility"]
        if volatility > 0.3:  # 30% annualized volatility
            recommendations.append("High volatility detected - Use wider stops and smaller positions")
            recommendations.append("Consider volatility-based strategies (Squeeze, Straddles)")
        elif volatility < 0.1:
            recommendations.append("Low volatility - Prepare for potential breakout")
            recommendations.append("Avoid mean reversion strategies in this environment")
        
        # Strategy-specific recommendations
        profitable_strategies = [r for r in results if r["evaluation"]["is_profitable"]]
        
        if len(profitable_strategies) >= 3:
            recommendations.append(f"Multiple profitable strategies found - Consider portfolio approach")
            
            # Find complementary strategies
            strategy_types = set(s["type"] for s in profitable_strategies)
            if "trend_following" in strategy_types and "mean_reversion" in strategy_types:
                recommendations.append("Combine trend + mean reversion for market regime adaptation")
        
        elif len(profitable_strategies) == 0:
            recommendations.append("No profitable strategies in current conditions")
            recommendations.append("Wait for better market structure or adjust parameters")
        
        # Best strategy deployment
        if self.current_best_strategy and self.current_best_strategy["evaluation"]["score"] >= 80:
            recommendations.append(f"Deploy {self.current_best_strategy['name']} with real capital")
            recommendations.append(f"Expected return: {self.current_best_strategy['backtest']['total_pnl_percent']:.1f}%")
        
        return recommendations
    
    def _save_research(self, cycle: int, report: Dict):
        """Save research results"""
        filename = self.research_dir / f"cycle_{cycle}_strategy_research.json"
        # Convert numpy types to Python native types
        serializable_report = self._convert_numpy_types(report)
        with open(filename, 'w') as f:
            json.dump(serializable_report, f, indent=2)
    
    def get_strategy_progress(self) -> Dict:
        """Get overall strategy development progress"""
        all_strategies = self.strategy_developer.get_best_strategies(min_score=0)
        profitable = self.strategy_developer.get_best_strategies(min_score=60)
        excellent = self.strategy_developer.get_best_strategies(min_score=80)
        
        progress = {
            "total_strategies_tested": len(all_strategies),
            "profitable_strategies": len(profitable),
            "excellent_strategies": len(excellent),
            "current_best": self.current_best_strategy,
            "ready_for_deployment": len(excellent) > 0
        }
        
        return progress
    
    def get_live_signals(self, current_price: float) -> List[Dict]:
        """Get live trading signals from best strategies"""
        signals = []
        
        # Get recent price data
        prices, timestamps = self.data_collector.get_latest_prices(100)
        
        if not prices or len(prices) < 50:
            return signals
        
        # Add current price
        prices.append(current_price)
        timestamps.append(datetime.now().isoformat())
        
        # Get top strategies
        top_strategies = self.strategy_developer.get_best_strategies(min_score=70)[:3]
        
        for strategy_result in top_strategies:
            # Recreate strategy
            strategy_func = getattr(self.strategy_developer, 
                                  f"_create_{strategy_result['name'].lower()}_strategy", 
                                  None)
            
            if strategy_func:
                strategy = strategy_func(prices, timestamps)
                
                if strategy and strategy["signals"]:
                    # Check if latest index has a signal
                    latest_signal = strategy["signals"].get(len(prices) - 1)
                    
                    if latest_signal:
                        signals.append({
                            "strategy": strategy_result["name"],
                            "signal": latest_signal,
                            "confidence": strategy_result["evaluation"]["score"] / 100,
                            "expected_win_rate": strategy_result["backtest"]["win_rate"]
                        })
        
        return signals
    
    def _convert_numpy_types(self, obj):
        """Recursively convert numpy types to Python native types"""
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.int_, np.intc, np.intp, np.int8, np.int16, np.int32, np.int64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._convert_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_numpy_types(item) for item in obj]
        else:
            return obj


def generate_strategy_research_prompt(cycle: int, progress: Dict, market_conditions: Dict) -> str:
    """Generate prompt for strategy-focused research"""
    
    prompt = f"""Cycle {cycle}: Advanced Trading Strategy Research

Current Progress:
- Strategies tested: {progress['total_strategies_tested']}
- Profitable strategies: {progress['profitable_strategies']}
- Deployment ready: {'YES' if progress['ready_for_deployment'] else 'NO'}

Market Conditions:
- Volatility: {market_conditions.get('volatility', 0):.1%}
- Trend: {market_conditions.get('trend', 0):.1%}

Your task:
1. Get current price data via MCP
2. Analyze market structure for strategy opportunities
3. Consider these advanced strategies:
   - Pairs trading (SOL/BTC correlation)
   - Options strategies (if volatility > 20%)
   - Arbitrage opportunities
   - Machine learning predictions
4. Generate specific, testable strategy rules
5. Provide exact entry/exit criteria
6. Include risk management rules

Focus on PROFITABILITY. We need strategies with:
- Win rate > 50%
- Profit factor > 1.5
- Sharpe ratio > 1.0
- Max drawdown < 20%

Be specific with numbers, not vague descriptions."""
    
    if progress['current_best']:
        prompt += f"""

Current best strategy: {progress['current_best']['name']}
- Score: {progress['current_best']['evaluation']['score']}/100
- Win rate: {progress['current_best']['backtest']['win_rate']:.1f}%

Try to beat this performance."""
    
    return prompt
"""
Advanced Research Engine for Self-Improving Analysis
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import statistics


class ResearchEngine:
    """Intelligent research engine that builds progressive insights"""
    
    def __init__(self):
        self.findings_dir = Path("knowledge/research/findings")
        self.insights_file = Path("knowledge/research/insights.json")
        self.mcp_cache_file = Path("knowledge/mcp_cache.json")
        self._load_cache()
        
    def _load_cache(self):
        """Load MCP connection cache"""
        self.mcp_cache = {}
        if self.mcp_cache_file.exists():
            with open(self.mcp_cache_file) as f:
                self.mcp_cache = json.load(f)
    
    def save_mcp_cache(self, server_id: str, server_url: str, wallet_address: str):
        """Cache MCP connection details to avoid repetitive discovery"""
        self.mcp_cache = {
            "server_id": server_id,
            "server_url": server_url,
            "wallet_address": wallet_address,
            "last_updated": datetime.now().isoformat()
        }
        self.mcp_cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.mcp_cache_file, 'w') as f:
            json.dump(self.mcp_cache, f, indent=2)
    
    def get_mcp_cache(self) -> Optional[Dict]:
        """Get cached MCP details if available"""
        if self.mcp_cache and "server_id" in self.mcp_cache:
            return self.mcp_cache
        return None
    
    def analyze_price_history(self, current_price: float, cycle: int) -> Dict[str, Any]:
        """Perform deep analysis on price history"""
        # Load all previous findings
        price_history = []
        timestamps = []
        
        for f in sorted(self.findings_dir.glob("cycle_*_market_analysis.json")):
            try:
                with open(f) as file:
                    data = json.load(file)
                    if 'price' in data:
                        price_history.append(data['price'])
                        timestamps.append(data.get('timestamp', ''))
            except:
                pass
        
        # Add current price
        price_history.append(current_price)
        timestamps.append(datetime.now().isoformat())
        
        analysis = {
            "current_price": current_price,
            "price_history": price_history[-20:],  # Last 20 prices
            "timestamps": timestamps[-20:]
        }
        
        if len(price_history) >= 2:
            # Calculate metrics
            analysis["price_change"] = current_price - price_history[-2]
            analysis["price_change_pct"] = ((current_price - price_history[-2]) / price_history[-2]) * 100
            
            if len(price_history) >= 3:
                # Moving averages
                analysis["ma_3"] = statistics.mean(price_history[-3:])
                analysis["ma_5"] = statistics.mean(price_history[-5:]) if len(price_history) >= 5 else None
                analysis["ma_10"] = statistics.mean(price_history[-10:]) if len(price_history) >= 10 else None
                
                # Volatility
                if len(price_history) >= 5:
                    analysis["volatility"] = statistics.stdev(price_history[-5:])
                    analysis["volatility_pct"] = (analysis["volatility"] / statistics.mean(price_history[-5:])) * 100
                
                # Trend detection
                if len(price_history) >= 5:
                    recent_prices = price_history[-5:]
                    trend_direction = "up" if recent_prices[-1] > recent_prices[0] else "down"
                    trend_strength = abs(recent_prices[-1] - recent_prices[0]) / recent_prices[0] * 100
                    analysis["trend"] = {
                        "direction": trend_direction,
                        "strength": trend_strength,
                        "consecutive_moves": self._count_consecutive_moves(price_history)
                    }
                
                # Support and resistance
                if len(price_history) >= 10:
                    analysis["support"] = min(price_history[-10:])
                    analysis["resistance"] = max(price_history[-10:])
                    analysis["current_position"] = (current_price - analysis["support"]) / (analysis["resistance"] - analysis["support"])
        
        return analysis
    
    def _count_consecutive_moves(self, prices: List[float]) -> int:
        """Count consecutive price moves in same direction"""
        if len(prices) < 2:
            return 0
        
        count = 0
        direction = None
        
        for i in range(len(prices) - 1, 0, -1):
            move = "up" if prices[i] > prices[i-1] else "down"
            if direction is None:
                direction = move
            if move == direction:
                count += 1
            else:
                break
        
        return count if direction == "up" else -count
    
    def generate_trading_signals(self, analysis: Dict) -> List[Dict]:
        """Generate actionable trading signals based on analysis"""
        signals = []
        
        if "ma_3" in analysis and "ma_5" in analysis and analysis["ma_5"]:
            # Moving average crossover
            if analysis["current_price"] > analysis["ma_3"] > analysis["ma_5"]:
                signals.append({
                    "type": "bullish_ma_crossover",
                    "strength": "medium",
                    "action": "consider_long",
                    "reason": "Price above short-term MAs with bullish alignment"
                })
            elif analysis["current_price"] < analysis["ma_3"] < analysis["ma_5"]:
                signals.append({
                    "type": "bearish_ma_crossover", 
                    "strength": "medium",
                    "action": "consider_short",
                    "reason": "Price below short-term MAs with bearish alignment"
                })
        
        if "trend" in analysis:
            # Trend following
            if analysis["trend"]["direction"] == "up" and analysis["trend"]["strength"] > 2:
                signals.append({
                    "type": "strong_uptrend",
                    "strength": "high" if analysis["trend"]["strength"] > 5 else "medium",
                    "action": "trend_following_long",
                    "reason": f"Strong uptrend with {analysis['trend']['strength']:.1f}% move"
                })
            
            # Momentum exhaustion
            consecutive = analysis["trend"]["consecutive_moves"]
            if abs(consecutive) >= 5:
                signals.append({
                    "type": "momentum_exhaustion",
                    "strength": "medium",
                    "action": "consider_reversal",
                    "reason": f"{abs(consecutive)} consecutive moves in same direction"
                })
        
        if "support" in analysis and "resistance" in analysis:
            # Support/Resistance levels
            position = analysis["current_position"]
            if position < 0.2:
                signals.append({
                    "type": "near_support",
                    "strength": "high",
                    "action": "bounce_play",
                    "reason": f"Price near support at ${analysis['support']:.2f}"
                })
            elif position > 0.8:
                signals.append({
                    "type": "near_resistance",
                    "strength": "high", 
                    "action": "resistance_short",
                    "reason": f"Price near resistance at ${analysis['resistance']:.2f}"
                })
        
        if "volatility_pct" in analysis:
            # Volatility-based signals
            if analysis["volatility_pct"] > 5:
                signals.append({
                    "type": "high_volatility",
                    "strength": "medium",
                    "action": "reduce_position_size",
                    "reason": f"Volatility at {analysis['volatility_pct']:.1f}% - above normal"
                })
            elif analysis["volatility_pct"] < 1:
                signals.append({
                    "type": "low_volatility",
                    "strength": "low",
                    "action": "await_breakout",
                    "reason": "Low volatility - potential breakout brewing"
                })
        
        return signals
    
    def suggest_next_research(self, current_analysis: Dict, cycle: int) -> List[Dict]:
        """Suggest next research topics based on current findings"""
        suggestions = []
        
        # Always suggest some advanced research after basic price analysis
        if cycle < 5:
            suggestions.append({
                "topic": "volume_analysis",
                "priority": "high",
                "reason": "Need volume data to confirm price movements"
            })
        
        if "trend" in current_analysis and current_analysis["trend"]["strength"] > 3:
            suggestions.append({
                "topic": "correlation_analysis",
                "priority": "medium",
                "reason": "Strong trend detected - check correlations with BTC/ETH"
            })
        
        if "volatility_pct" in current_analysis and current_analysis["volatility_pct"] > 4:
            suggestions.append({
                "topic": "news_sentiment",
                "priority": "high",
                "reason": "High volatility detected - check for news catalysts"
            })
        
        if cycle > 10 and cycle % 10 == 0:
            suggestions.append({
                "topic": "arbitrage_scan",
                "priority": "medium",
                "reason": "Periodic arbitrage opportunity scan"
            })
        
        if "support" in current_analysis and "resistance" in current_analysis:
            range_size = (current_analysis["resistance"] - current_analysis["support"]) / current_analysis["support"] * 100
            if range_size < 5:
                suggestions.append({
                    "topic": "breakout_analysis",
                    "priority": "high",
                    "reason": f"Tight {range_size:.1f}% range - breakout imminent"
                })
        
        return suggestions
    
    def evolve_goals(self, current_goals: List[Dict], analysis: Dict, signals: List[Dict]) -> List[Dict]:
        """Evolve goals based on current findings"""
        evolved_goals = []
        
        # Keep existing high-priority goals
        for goal in current_goals:
            if goal.get("priority") == "high" and goal.get("progress", 0) < 80:
                evolved_goals.append(goal)
        
        # Add new goals based on signals
        if any(s["type"] == "strong_uptrend" for s in signals):
            evolved_goals.append({
                "id": f"goal_trend_{datetime.now().strftime('%H%M%S')}",
                "title": "Uptrend Momentum Analysis",
                "description": "Deep dive into current uptrend sustainability and targets",
                "status": "active",
                "priority": "high",
                "created_at": datetime.now().isoformat(),
                "progress": 0,
                "metrics": ["trend_continuation", "volume_confirmation", "resistance_levels"]
            })
        
        if any(s["type"] == "high_volatility" for s in signals):
            evolved_goals.append({
                "id": f"goal_vol_{datetime.now().strftime('%H%M%S')}",
                "title": "Volatility Trading Strategy",
                "description": "Develop strategies to profit from current high volatility",
                "status": "active",
                "priority": "medium",
                "created_at": datetime.now().isoformat(),
                "progress": 0,
                "metrics": ["volatility_prediction", "option_strategies", "risk_management"]
            })
        
        # Limit to top 5 goals
        evolved_goals = sorted(evolved_goals, key=lambda x: (x["priority"] == "high", -x.get("progress", 0)))[:5]
        
        return evolved_goals
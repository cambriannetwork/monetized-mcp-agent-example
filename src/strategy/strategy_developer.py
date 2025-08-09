"""
Strategy Developer - Creates and tests trading strategies
"""

import json
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from pathlib import Path

from .backtester import Backtester, BacktestResult, evaluate_strategy_profitability


class StrategyDeveloper:
    """Develops and tests trading strategies using price data"""
    
    def __init__(self):
        self.strategies_dir = Path("knowledge/strategies")
        self.strategies_dir.mkdir(parents=True, exist_ok=True)
        self.tested_strategies = []
        self._load_strategy_history()
    
    def _load_strategy_history(self):
        """Load previously tested strategies"""
        history_file = self.strategies_dir / "strategy_history.json"
        if history_file.exists():
            with open(history_file) as f:
                self.tested_strategies = json.load(f)
    
    def _save_strategy_history(self):
        """Save strategy test results"""
        history_file = self.strategies_dir / "strategy_history.json"
        # Convert numpy types to Python native types for JSON serialization
        serializable_strategies = self._convert_numpy_types(self.tested_strategies)
        with open(history_file, 'w') as f:
            json.dump(serializable_strategies, f, indent=2)
    
    def develop_strategies(self, prices: List[float], timestamps: List[str]) -> List[Dict]:
        """
        Develop multiple trading strategies based on price data
        
        Returns list of strategies with signals
        """
        strategies = []
        
        # Strategy 1: Moving Average Crossover
        ma_strategy = self._create_ma_crossover_strategy(prices, timestamps)
        if ma_strategy:
            strategies.append(ma_strategy)
        
        # Strategy 2: Support/Resistance Breakout
        breakout_strategy = self._create_breakout_strategy(prices, timestamps)
        if breakout_strategy:
            strategies.append(breakout_strategy)
        
        # Strategy 3: Momentum Reversal
        reversal_strategy = self._create_reversal_strategy(prices, timestamps)
        if reversal_strategy:
            strategies.append(reversal_strategy)
        
        # Strategy 4: Volatility Squeeze
        squeeze_strategy = self._create_volatility_squeeze_strategy(prices, timestamps)
        if squeeze_strategy:
            strategies.append(squeeze_strategy)
        
        # Strategy 5: Mean Reversion
        mean_reversion = self._create_mean_reversion_strategy(prices, timestamps)
        if mean_reversion:
            strategies.append(mean_reversion)
        
        return strategies
    
    def _create_ma_crossover_strategy(self, prices: List[float], timestamps: List[str]) -> Optional[Dict]:
        """Create moving average crossover strategy"""
        if len(prices) < 20:
            return None
        
        # Calculate moving averages
        ma_fast = self._calculate_ma(prices, 5)
        ma_slow = self._calculate_ma(prices, 15)
        
        signals = {}
        
        for i in range(15, len(prices)):
            # Bullish crossover
            if i > 0 and ma_fast[i-1] <= ma_slow[i-1] and ma_fast[i] > ma_slow[i]:
                # Calculate stop and target
                atr = self._calculate_atr(prices[:i+1], 14)
                signals[i] = {
                    "action": "buy",
                    "stop": prices[i] - (2 * atr),
                    "target": prices[i] + (3 * atr),
                    "reason": "MA crossover bullish"
                }
            
            # Bearish crossover
            elif i > 0 and ma_fast[i-1] >= ma_slow[i-1] and ma_fast[i] < ma_slow[i]:
                atr = self._calculate_atr(prices[:i+1], 14)
                signals[i] = {
                    "action": "sell",
                    "stop": prices[i] + (2 * atr),
                    "target": prices[i] - (3 * atr),
                    "reason": "MA crossover bearish"
                }
        
        return {
            "name": "MA_Crossover_5_15",
            "type": "trend_following",
            "signals": signals,
            "parameters": {"fast_ma": 5, "slow_ma": 15}
        }
    
    def _create_breakout_strategy(self, prices: List[float], timestamps: List[str]) -> Optional[Dict]:
        """Create support/resistance breakout strategy"""
        if len(prices) < 20:
            return None
        
        signals = {}
        lookback = 20
        
        for i in range(lookback, len(prices)):
            recent_prices = prices[i-lookback:i]
            resistance = max(recent_prices)
            support = min(recent_prices)
            
            # Breakout above resistance
            if prices[i] > resistance * 1.01:  # 1% above resistance
                atr = self._calculate_atr(prices[:i+1], 14)
                signals[i] = {
                    "action": "buy",
                    "stop": resistance - (0.5 * atr),
                    "target": prices[i] + (2 * atr),
                    "reason": f"Breakout above {resistance:.2f}"
                }
            
            # Breakdown below support
            elif prices[i] < support * 0.99:  # 1% below support
                atr = self._calculate_atr(prices[:i+1], 14)
                signals[i] = {
                    "action": "sell",
                    "stop": support + (0.5 * atr),
                    "target": prices[i] - (2 * atr),
                    "reason": f"Breakdown below {support:.2f}"
                }
        
        return {
            "name": "Breakout_20",
            "type": "momentum",
            "signals": signals,
            "parameters": {"lookback": lookback}
        }
    
    def _create_reversal_strategy(self, prices: List[float], timestamps: List[str]) -> Optional[Dict]:
        """Create momentum reversal strategy"""
        if len(prices) < 10:
            return None
        
        signals = {}
        
        for i in range(5, len(prices)):
            # Check for exhaustion after strong moves
            recent_change = (prices[i] - prices[i-5]) / prices[i-5] * 100
            
            # Overbought reversal
            if recent_change > 5:  # 5% move in 5 periods
                rsi = self._calculate_rsi(prices[:i+1], 14)
                if rsi and rsi > 70:
                    atr = self._calculate_atr(prices[:i+1], 14)
                    signals[i] = {
                        "action": "sell",
                        "stop": prices[i] + atr,
                        "target": prices[i] - (2 * atr),
                        "reason": f"Overbought reversal (RSI: {rsi:.1f})"
                    }
            
            # Oversold reversal
            elif recent_change < -5:  # -5% move in 5 periods
                rsi = self._calculate_rsi(prices[:i+1], 14)
                if rsi and rsi < 30:
                    atr = self._calculate_atr(prices[:i+1], 14)
                    signals[i] = {
                        "action": "buy",
                        "stop": prices[i] - atr,
                        "target": prices[i] + (2 * atr),
                        "reason": f"Oversold reversal (RSI: {rsi:.1f})"
                    }
        
        return {
            "name": "Momentum_Reversal",
            "type": "mean_reversion",
            "signals": signals,
            "parameters": {"rsi_overbought": 70, "rsi_oversold": 30}
        }
    
    def _create_volatility_squeeze_strategy(self, prices: List[float], timestamps: List[str]) -> Optional[Dict]:
        """Create volatility squeeze breakout strategy"""
        if len(prices) < 20:
            return None
        
        signals = {}
        
        for i in range(20, len(prices)):
            # Calculate Bollinger Bands
            bb_period = 20
            recent_prices = prices[i-bb_period:i]
            ma = np.mean(recent_prices)
            std = np.std(recent_prices)
            
            upper_band = ma + (2 * std)
            lower_band = ma - (2 * std)
            band_width = (upper_band - lower_band) / ma
            
            # Look for squeeze (low volatility)
            if i > bb_period + 5:
                prev_widths = []
                for j in range(5):
                    prev_prices = prices[i-bb_period-j:i-j]
                    prev_std = np.std(prev_prices)
                    prev_width = (4 * prev_std) / np.mean(prev_prices)
                    prev_widths.append(prev_width)
                
                avg_width = np.mean(prev_widths)
                
                # Volatility squeeze detected
                if band_width < avg_width * 0.7:
                    # Wait for breakout direction
                    if prices[i] > upper_band:
                        atr = self._calculate_atr(prices[:i+1], 14)
                        signals[i] = {
                            "action": "buy",
                            "stop": ma,
                            "target": prices[i] + (3 * atr),
                            "reason": "Volatility squeeze breakout UP"
                        }
                    elif prices[i] < lower_band:
                        atr = self._calculate_atr(prices[:i+1], 14)
                        signals[i] = {
                            "action": "sell",
                            "stop": ma,
                            "target": prices[i] - (3 * atr),
                            "reason": "Volatility squeeze breakout DOWN"
                        }
        
        return {
            "name": "Volatility_Squeeze",
            "type": "volatility",
            "signals": signals,
            "parameters": {"bb_period": 20, "bb_std": 2}
        }
    
    def _create_mean_reversion_strategy(self, prices: List[float], timestamps: List[str]) -> Optional[Dict]:
        """Create mean reversion strategy"""
        if len(prices) < 50:
            return None
        
        signals = {}
        period = 50
        
        for i in range(period, len(prices)):
            ma = np.mean(prices[i-period:i])
            std = np.std(prices[i-period:i])
            z_score = (prices[i] - ma) / std if std > 0 else 0
            
            # Extreme deviation from mean
            if z_score > 2:  # 2 standard deviations above
                atr = self._calculate_atr(prices[:i+1], 14)
                signals[i] = {
                    "action": "sell",
                    "stop": prices[i] + atr,
                    "target": ma,
                    "reason": f"Mean reversion short (Z: {z_score:.1f})"
                }
            elif z_score < -2:  # 2 standard deviations below
                atr = self._calculate_atr(prices[:i+1], 14)
                signals[i] = {
                    "action": "buy", 
                    "stop": prices[i] - atr,
                    "target": ma,
                    "reason": f"Mean reversion long (Z: {z_score:.1f})"
                }
        
        return {
            "name": "Mean_Reversion_50",
            "type": "mean_reversion",
            "signals": signals,
            "parameters": {"period": period, "z_threshold": 2}
        }
    
    def test_strategies(self, strategies: List[Dict], prices: List[float], timestamps: List[str]) -> List[Dict]:
        """Test strategies and return results"""
        results = []
        
        for strategy in strategies:
            backtester = Backtester()
            result = backtester.backtest_strategy(prices, timestamps, strategy["signals"])
            evaluation = evaluate_strategy_profitability(result)
            
            strategy_result = {
                "name": strategy["name"],
                "type": strategy["type"],
                "parameters": strategy["parameters"],
                "backtest": {
                    "total_trades": result.total_trades,
                    "win_rate": result.win_rate,
                    "profit_factor": result.profit_factor,
                    "total_pnl_percent": result.total_pnl_percent,
                    "sharpe_ratio": result.sharpe_ratio,
                    "max_drawdown": result.max_drawdown
                },
                "evaluation": evaluation,
                "tested_on": datetime.now().isoformat()
            }
            
            results.append(strategy_result)
            self.tested_strategies.append(strategy_result)
        
        # Save history
        self._save_strategy_history()
        
        return results
    
    def get_best_strategies(self, min_score: float = 60) -> List[Dict]:
        """Get strategies that meet minimum profitability criteria"""
        profitable = []
        
        for strategy in self.tested_strategies:
            if strategy["evaluation"]["score"] >= min_score:
                profitable.append(strategy)
        
        # Sort by score
        profitable.sort(key=lambda x: x["evaluation"]["score"], reverse=True)
        
        return profitable
    
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
    
    # Helper methods
    def _calculate_ma(self, prices: List[float], period: int) -> List[float]:
        """Calculate moving average"""
        ma = []
        for i in range(len(prices)):
            if i < period - 1:
                ma.append(prices[i])
            else:
                ma.append(np.mean(prices[i-period+1:i+1]))
        return ma
    
    def _calculate_atr(self, prices: List[float], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(prices) < period + 1:
            return np.std(prices[-min(len(prices), 5):]) if len(prices) > 1 else 0
        
        true_ranges = []
        for i in range(1, len(prices)):
            high = prices[i]
            low = prices[i]
            prev_close = prices[i-1]
            
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            true_ranges.append(tr)
        
        if len(true_ranges) >= period:
            return np.mean(true_ranges[-period:])
        else:
            return np.mean(true_ranges) if true_ranges else 0
    
    def _calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return None
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if len(gains) < period:
            return None
        
        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
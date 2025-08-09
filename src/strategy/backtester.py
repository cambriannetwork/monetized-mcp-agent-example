"""
Trading Strategy Backtester
Tests trading strategies on historical price data
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trade:
    """Represents a single trade"""
    entry_time: datetime
    entry_price: float
    exit_time: Optional[datetime] = None
    exit_price: Optional[float] = None
    position_size: float = 1.0
    side: str = "long"  # "long" or "short"
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    @property
    def is_open(self) -> bool:
        return self.exit_time is None
    
    @property
    def pnl(self) -> float:
        if not self.exit_price:
            return 0.0
        
        if self.side == "long":
            return (self.exit_price - self.entry_price) * self.position_size
        else:
            return (self.entry_price - self.exit_price) * self.position_size
    
    @property
    def pnl_percent(self) -> float:
        if not self.exit_price:
            return 0.0
        
        if self.side == "long":
            return ((self.exit_price - self.entry_price) / self.entry_price) * 100
        else:
            return ((self.entry_price - self.exit_price) / self.entry_price) * 100


@dataclass
class BacktestResult:
    """Results from a backtest"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_pnl: float
    total_pnl_percent: float
    win_rate: float
    avg_win: float
    avg_loss: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown: float
    trades: List[Trade]
    equity_curve: List[float]


class Backtester:
    """Backtests trading strategies on price data"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trades: List[Trade] = []
        self.equity_curve: List[float] = [initial_capital]
        
    def backtest_strategy(self, 
                         prices: List[float], 
                         timestamps: List[str],
                         strategy_signals: Dict[int, Dict]) -> BacktestResult:
        """
        Backtest a strategy given price data and signals
        
        Args:
            prices: List of prices
            timestamps: List of timestamps
            strategy_signals: Dict mapping price index to signal
                             e.g. {5: {"action": "buy", "stop": 180, "target": 190}}
        
        Returns:
            BacktestResult with performance metrics
        """
        current_trade = None
        
        for i, (price, timestamp) in enumerate(zip(prices, timestamps)):
            # Check for exit conditions on open trade
            if current_trade and current_trade.is_open:
                should_exit = False
                exit_reason = ""
                
                # Check stop loss
                if current_trade.stop_loss:
                    if current_trade.side == "long" and price <= current_trade.stop_loss:
                        should_exit = True
                        exit_reason = "stop_loss"
                    elif current_trade.side == "short" and price >= current_trade.stop_loss:
                        should_exit = True
                        exit_reason = "stop_loss"
                
                # Check take profit
                if current_trade.take_profit and not should_exit:
                    if current_trade.side == "long" and price >= current_trade.take_profit:
                        should_exit = True
                        exit_reason = "take_profit"
                    elif current_trade.side == "short" and price <= current_trade.take_profit:
                        should_exit = True
                        exit_reason = "take_profit"
                
                # Exit trade
                if should_exit:
                    current_trade.exit_time = timestamp
                    current_trade.exit_price = price
                    self.capital += current_trade.pnl
                    self.equity_curve.append(self.capital)
                    current_trade = None
            
            # Check for new signals
            if i in strategy_signals and not current_trade:
                signal = strategy_signals[i]
                action = signal.get("action")
                
                if action in ["buy", "long"]:
                    current_trade = Trade(
                        entry_time=timestamp,
                        entry_price=price,
                        side="long",
                        stop_loss=signal.get("stop"),
                        take_profit=signal.get("target"),
                        position_size=self._calculate_position_size(price, signal.get("stop"))
                    )
                    self.trades.append(current_trade)
                    
                elif action in ["sell", "short"]:
                    current_trade = Trade(
                        entry_time=timestamp,
                        entry_price=price,
                        side="short",
                        stop_loss=signal.get("stop"),
                        take_profit=signal.get("target"),
                        position_size=self._calculate_position_size(price, signal.get("stop"))
                    )
                    self.trades.append(current_trade)
        
        # Close any open trades at the end
        if current_trade and current_trade.is_open:
            current_trade.exit_time = timestamps[-1]
            current_trade.exit_price = prices[-1]
            self.capital += current_trade.pnl
            self.equity_curve.append(self.capital)
        
        # Calculate metrics
        return self._calculate_metrics()
    
    def _calculate_position_size(self, price: float, stop_loss: Optional[float]) -> float:
        """Calculate position size based on risk management"""
        if not stop_loss:
            # Default to 10% of capital
            return (self.capital * 0.1) / price
        
        # Risk 2% of capital per trade
        risk_amount = self.capital * 0.02
        risk_per_share = abs(price - stop_loss)
        
        if risk_per_share > 0:
            return risk_amount / risk_per_share
        else:
            return (self.capital * 0.1) / price
    
    def _calculate_metrics(self) -> BacktestResult:
        """Calculate backtest performance metrics"""
        closed_trades = [t for t in self.trades if not t.is_open]
        
        if not closed_trades:
            return BacktestResult(
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                total_pnl=0,
                total_pnl_percent=0,
                win_rate=0,
                avg_win=0,
                avg_loss=0,
                profit_factor=0,
                sharpe_ratio=0,
                max_drawdown=0,
                trades=self.trades,
                equity_curve=self.equity_curve
            )
        
        # Basic metrics
        winning_trades = [t for t in closed_trades if t.pnl > 0]
        losing_trades = [t for t in closed_trades if t.pnl < 0]
        
        total_pnl = sum(t.pnl for t in closed_trades)
        total_pnl_percent = ((self.capital - self.initial_capital) / self.initial_capital) * 100
        
        win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0
        avg_win = np.mean([t.pnl for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([abs(t.pnl) for t in losing_trades]) if losing_trades else 0
        
        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
        gross_loss = sum(abs(t.pnl) for t in losing_trades) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Sharpe ratio (simplified)
        returns = np.diff(self.equity_curve) / self.equity_curve[:-1]
        sharpe_ratio = np.sqrt(252) * np.mean(returns) / np.std(returns) if len(returns) > 1 and np.std(returns) > 0 else 0
        
        # Max drawdown
        peak = self.initial_capital
        max_dd = 0
        for value in self.equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak
            if dd > max_dd:
                max_dd = dd
        
        return BacktestResult(
            total_trades=len(closed_trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            total_pnl=total_pnl,
            total_pnl_percent=total_pnl_percent,
            win_rate=win_rate * 100,
            avg_win=avg_win,
            avg_loss=avg_loss,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown=max_dd * 100,
            trades=self.trades,
            equity_curve=self.equity_curve
        )


def evaluate_strategy_profitability(result: BacktestResult) -> Dict[str, any]:
    """Evaluate if a strategy is profitable and worth pursuing"""
    
    evaluation = {
        "is_profitable": bool(result.total_pnl > 0),
        "is_robust": bool(result.win_rate > 40 and result.profit_factor > 1.5),
        "is_consistent": bool(result.sharpe_ratio > 1.0),
        "risk_acceptable": bool(result.max_drawdown < 20),
        "score": 0.0,
        "recommendation": ""
    }
    
    # Calculate overall score
    score = 0.0
    if evaluation["is_profitable"]:
        score += 25
    if result.win_rate > 50:
        score += 25
    if result.profit_factor > 2:
        score += 25
    if result.sharpe_ratio > 1.5:
        score += 15
    if result.max_drawdown < 15:
        score += 10
    
    evaluation["score"] = score
    
    # Recommendation
    if score >= 80:
        evaluation["recommendation"] = "EXCELLENT - Deploy with real capital"
    elif score >= 60:
        evaluation["recommendation"] = "GOOD - Further optimization recommended"
    elif score >= 40:
        evaluation["recommendation"] = "MARGINAL - Needs significant improvement"
    else:
        evaluation["recommendation"] = "POOR - Abandon or completely redesign"
    
    return evaluation
#!/usr/bin/env python3
"""Test numpy type conversion for JSON serialization"""

import json
import numpy as np
from src.strategy.backtester import BacktestResult, evaluate_strategy_profitability
from src.strategy.strategy_developer import StrategyDeveloper

def test_numpy_conversion():
    """Test that numpy types are properly converted"""
    
    # Create a fake BacktestResult with numpy types
    result = BacktestResult(
        total_trades=10,
        winning_trades=6,
        losing_trades=4,
        total_pnl=np.float64(1000.0),
        total_pnl_percent=np.float64(10.0),
        win_rate=np.float64(60.0),
        avg_win=np.float64(200.0),
        avg_loss=np.float64(100.0),
        profit_factor=np.float64(2.0),
        sharpe_ratio=np.float64(1.5),
        max_drawdown=np.float64(15.0),
        trades=[],
        equity_curve=[]
    )
    
    # Test evaluation function
    evaluation = evaluate_strategy_profitability(result)
    
    print("Evaluation result:")
    print(f"  is_profitable: {evaluation['is_profitable']} (type: {type(evaluation['is_profitable'])})")
    print(f"  is_robust: {evaluation['is_robust']} (type: {type(evaluation['is_robust'])})")
    print(f"  score: {evaluation['score']} (type: {type(evaluation['score'])})")
    
    # Test JSON serialization
    try:
        json_str = json.dumps(evaluation)
        print("\n✅ JSON serialization successful!")
        print(f"JSON: {json_str}")
    except Exception as e:
        print(f"\n❌ JSON serialization failed: {e}")
        return False
    
    # Test StrategyDeveloper conversion
    developer = StrategyDeveloper()
    test_data = {
        "name": "Test Strategy",
        "backtest": {
            "win_rate": np.float64(55.5),
            "total_pnl": np.float64(1234.56)
        },
        "evaluation": {
            "is_profitable": np.bool_(True),
            "score": np.float64(75.0)
        }
    }
    
    converted = developer._convert_numpy_types(test_data)
    print("\n\nConverted data:")
    print(f"  is_profitable: {converted['evaluation']['is_profitable']} (type: {type(converted['evaluation']['is_profitable'])})")
    print(f"  win_rate: {converted['backtest']['win_rate']} (type: {type(converted['backtest']['win_rate'])})")
    
    try:
        json_str = json.dumps(converted)
        print("\n✅ Converted data JSON serialization successful!")
        return True
    except Exception as e:
        print(f"\n❌ Converted data JSON serialization failed: {e}")
        return False

if __name__ == "__main__":
    success = test_numpy_conversion()
    exit(0 if success else 1)
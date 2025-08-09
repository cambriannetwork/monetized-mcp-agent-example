"""
MCP Data Collector - Programmatically collects price data for strategy development
"""

import asyncio
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path


class MCPDataCollector:
    """Collects historical price data via MCP for backtesting"""
    
    def __init__(self):
        self.data_dir = Path("knowledge/market_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.data_dir / "price_cache.json"
        self._load_cache()
    
    def _load_cache(self):
        """Load cached price data"""
        if self.cache_file.exists():
            with open(self.cache_file) as f:
                self.price_cache = json.load(f)
        else:
            self.price_cache = {
                "prices": [],
                "timestamps": [],
                "last_updated": None
            }
    
    def _save_cache(self):
        """Save price data to cache"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.price_cache, f, indent=2)
    
    async def collect_price_history(self, num_points: int = 100) -> Tuple[List[float], List[str]]:
        """
        Collect price history data points
        
        For now, returns cached/simulated data. In production, this would
        make actual MCP calls to get historical data.
        """
        # Check if we have enough cached data
        if len(self.price_cache["prices"]) >= num_points:
            return (
                self.price_cache["prices"][-num_points:],
                self.price_cache["timestamps"][-num_points:]
            )
        
        # In production, this would make MCP calls
        # For now, return simulated realistic price data
        prices, timestamps = self._generate_realistic_price_data(num_points)
        
        # Update cache
        self.price_cache["prices"].extend(prices)
        self.price_cache["timestamps"].extend(timestamps)
        self.price_cache["last_updated"] = datetime.now().isoformat()
        
        # Keep only last 1000 points in cache
        if len(self.price_cache["prices"]) > 1000:
            self.price_cache["prices"] = self.price_cache["prices"][-1000:]
            self.price_cache["timestamps"] = self.price_cache["timestamps"][-1000:]
        
        self._save_cache()
        
        return prices, timestamps
    
    def add_new_price(self, price: float, timestamp: Optional[str] = None):
        """Add a new price point to the cache"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        self.price_cache["prices"].append(price)
        self.price_cache["timestamps"].append(timestamp)
        self.price_cache["last_updated"] = timestamp
        
        # Keep cache size limited
        if len(self.price_cache["prices"]) > 1000:
            self.price_cache["prices"] = self.price_cache["prices"][-1000:]
            self.price_cache["timestamps"] = self.price_cache["timestamps"][-1000:]
        
        self._save_cache()
    
    def get_latest_prices(self, num_points: int = 50) -> Tuple[List[float], List[str]]:
        """Get the latest cached prices"""
        if len(self.price_cache["prices"]) >= num_points:
            return (
                self.price_cache["prices"][-num_points:],
                self.price_cache["timestamps"][-num_points:]
            )
        else:
            return (
                self.price_cache["prices"],
                self.price_cache["timestamps"]
            )
    
    def _generate_realistic_price_data(self, num_points: int) -> Tuple[List[float], List[str]]:
        """Generate realistic price data for testing"""
        import numpy as np
        
        # Start from a base price (e.g., current SOL price around 180)
        base_price = 180.0
        volatility = 0.02  # 2% daily volatility
        trend = 0.0001  # Slight upward trend
        
        prices = []
        timestamps = []
        
        current_price = base_price
        current_time = datetime.now() - timedelta(hours=num_points)
        
        for i in range(num_points):
            # Random walk with trend
            change = np.random.normal(trend, volatility)
            current_price *= (1 + change)
            
            # Add some mean reversion
            if current_price > base_price * 1.1:
                current_price *= 0.99
            elif current_price < base_price * 0.9:
                current_price *= 1.01
            
            prices.append(round(current_price, 2))
            timestamps.append(current_time.isoformat())
            
            current_time += timedelta(hours=1)
        
        return prices, timestamps
    
    async def collect_multi_token_data(self, tokens: List[str], num_points: int = 50) -> Dict[str, Dict]:
        """
        Collect data for multiple tokens
        
        In production, this would make MCP calls for each token
        """
        data = {}
        
        for token in tokens:
            # In production: Make MCP call for each token
            # For now: Generate correlated data
            if token == "SOL":
                prices, timestamps = await self.collect_price_history(num_points)
            elif token == "BTC":
                # Generate BTC data (correlated with SOL)
                sol_prices, timestamps = await self.collect_price_history(num_points)
                prices = [p * 250 for p in sol_prices]  # BTC ~250x SOL price
                prices = [p * (1 + np.random.normal(0, 0.01)) for p in prices]
            else:
                # Other tokens
                sol_prices, timestamps = await self.collect_price_history(num_points)
                prices = [p * np.random.uniform(0.1, 2.0) for p in sol_prices]
            
            data[token] = {
                "prices": prices,
                "timestamps": timestamps
            }
        
        return data


class MCPStrategyDataProvider:
    """Provides data for strategy development using MCP"""
    
    def __init__(self, mcp_cache: Optional[Dict] = None):
        self.collector = MCPDataCollector()
        self.mcp_cache = mcp_cache
    
    async def get_strategy_development_data(self) -> Dict:
        """Get comprehensive data for strategy development"""
        
        # Collect price history
        prices, timestamps = await self.collector.collect_price_history(100)
        
        # Calculate additional metrics
        returns = []
        for i in range(1, len(prices)):
            ret = (prices[i] - prices[i-1]) / prices[i-1]
            returns.append(ret)
        
        # Volume data (would come from MCP in production)
        volumes = [1000000 * (1 + np.random.uniform(-0.5, 0.5)) for _ in prices]
        
        # Market data
        data = {
            "prices": prices,
            "timestamps": timestamps,
            "returns": returns,
            "volumes": volumes,
            "metrics": {
                "avg_price": np.mean(prices),
                "volatility": np.std(returns) * np.sqrt(252) if returns else 0,
                "trend": (prices[-1] - prices[0]) / prices[0] if len(prices) > 1 else 0
            }
        }
        
        return data
    
    async def get_live_price(self) -> Optional[float]:
        """
        Get live price via MCP
        
        In production, this would make an actual MCP call
        For now, returns the latest cached price
        """
        prices, _ = self.collector.get_latest_prices(1)
        return prices[0] if prices else None


# Import numpy at module level
import numpy as np
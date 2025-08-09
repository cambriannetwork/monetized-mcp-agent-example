"""
REAL MCP Data Collector - NO SIMULATED DATA ALLOWED
This module ONLY works with real data from MCP purchases
"""

import json
from typing import List, Dict, Tuple, Optional
from datetime import datetime
from pathlib import Path


class RealMCPDataCollector:
    """Collects and stores ONLY REAL MCP price data"""
    
    def __init__(self):
        self.data_dir = Path("knowledge/real_mcp_data")
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.real_data_file = self.data_dir / "real_prices.json"
        self._load_real_data()
    
    def _load_real_data(self):
        """Load ONLY real MCP data"""
        if self.real_data_file.exists():
            with open(self.real_data_file) as f:
                self.real_data = json.load(f)
                print(f"✅ Loaded {len(self.real_data['prices'])} REAL price points")
        else:
            self.real_data = {
                "prices": [],
                "timestamps": [],
                "sources": [],  # Track where each price came from
                "last_mcp_update": None
            }
            print("⚠️  No real MCP data found. Must collect from MCP purchases!")
    
    def add_real_mcp_price(self, price: float, timestamp: str, source: str = "MCP"):
        """Add a REAL price from MCP - NO FAKE DATA"""
        if not isinstance(price, (int, float)) or price <= 0:
            raise ValueError(f"Invalid price: {price}. Must be positive number from real MCP!")
        
        self.real_data["prices"].append(float(price))
        self.real_data["timestamps"].append(timestamp)
        self.real_data["sources"].append(source)
        self.real_data["last_mcp_update"] = timestamp
        
        # Keep last 10000 real data points
        if len(self.real_data["prices"]) > 10000:
            self.real_data["prices"] = self.real_data["prices"][-10000:]
            self.real_data["timestamps"] = self.real_data["timestamps"][-10000:]
            self.real_data["sources"] = self.real_data["sources"][-10000:]
        
        self._save_real_data()
        print(f"✅ Added REAL price: ${price:.2f} from {source}")
    
    def _save_real_data(self):
        """Save real MCP data"""
        with open(self.real_data_file, 'w') as f:
            json.dump(self.real_data, f, indent=2)
    
    def get_real_prices(self, num_points: Optional[int] = None) -> Tuple[List[float], List[str]]:
        """Get REAL MCP prices only"""
        if not self.real_data["prices"]:
            raise ValueError(
                "NO REAL MCP DATA AVAILABLE! "
                "The agent must make MCP purchases to collect real price data. "
                "Simulated data has been REMOVED."
            )
        
        if num_points and len(self.real_data["prices"]) < num_points:
            raise ValueError(
                f"Insufficient REAL data! Have {len(self.real_data['prices'])} real points, "
                f"need {num_points}. Make more MCP purchases to collect data!"
            )
        
        if num_points:
            return (
                self.real_data["prices"][-num_points:],
                self.real_data["timestamps"][-num_points:]
            )
        else:
            return (
                self.real_data["prices"],
                self.real_data["timestamps"]
            )
    
    def clear_all_data(self):
        """Clear all data to start fresh with ONLY real MCP data"""
        self.real_data = {
            "prices": [],
            "timestamps": [],
            "sources": [],
            "last_mcp_update": None
        }
        self._save_real_data()
        print("🗑️  Cleared all data. Ready for REAL MCP data only!")
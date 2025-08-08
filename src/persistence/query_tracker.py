"""
Query Tracker for MCP Agent
Tracks successful MCP queries and their patterns for reuse
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import hashlib


class QueryTracker:
    """Tracks successful MCP queries and their patterns"""
    
    def __init__(self, storage_path: str = "knowledge/mcp_queries"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.successful_queries_file = self.storage_path / "successful_queries.json"
        self.query_patterns_file = self.storage_path / "query_patterns.json"
        self._load_data()
    
    def _load_data(self):
        """Load existing query data"""
        self.successful_queries = []
        self.query_patterns = {}
        
        if self.successful_queries_file.exists():
            with open(self.successful_queries_file) as f:
                self.successful_queries = json.load(f)
        
        if self.query_patterns_file.exists():
            with open(self.query_patterns_file) as f:
                self.query_patterns = json.load(f)
    
    def track_successful_query(self, 
                             tool_name: str,
                             tool_params: Dict[str, Any],
                             result: Any,
                             goal_type: str,
                             cycle_number: int):
        """Track a successful MCP query for future reference"""
        
        # Create query record
        query_record = {
            "id": self._generate_query_id(tool_name, tool_params),
            "timestamp": datetime.now().isoformat(),
            "cycle": cycle_number,
            "goal_type": goal_type,
            "tool": tool_name,
            "params": tool_params,
            "result_summary": self._summarize_result(result),
            "success": True
        }
        
        # Add to successful queries
        self.successful_queries.append(query_record)
        
        # Update patterns
        pattern_key = f"{goal_type}_{tool_name}"
        if pattern_key not in self.query_patterns:
            self.query_patterns[pattern_key] = {
                "goal_type": goal_type,
                "tool": tool_name,
                "successful_params": [],
                "success_rate": 1.0,
                "usage_count": 0
            }
        
        # Track successful parameters
        self.query_patterns[pattern_key]["successful_params"].append({
            "params": tool_params,
            "timestamp": query_record["timestamp"]
        })
        self.query_patterns[pattern_key]["usage_count"] += 1
        
        # Keep only recent patterns (last 10)
        if len(self.query_patterns[pattern_key]["successful_params"]) > 10:
            self.query_patterns[pattern_key]["successful_params"] = \
                self.query_patterns[pattern_key]["successful_params"][-10:]
        
        # Save data
        self._save_data()
    
    def get_successful_pattern(self, goal_type: str, tool_name: str) -> Optional[Dict]:
        """Get the most recent successful pattern for a goal/tool combination"""
        pattern_key = f"{goal_type}_{tool_name}"
        if pattern_key in self.query_patterns:
            pattern = self.query_patterns[pattern_key]
            if pattern["successful_params"]:
                return pattern["successful_params"][-1]["params"]
        return None
    
    def get_query_sequence_for_goal(self, goal_type: str) -> List[Dict]:
        """Get the typical sequence of queries for a goal type"""
        sequences = []
        
        # Filter queries by goal type
        goal_queries = [q for q in self.successful_queries if q["goal_type"] == goal_type]
        
        # Group by cycle to find patterns
        cycles = {}
        for query in goal_queries:
            cycle = query["cycle"]
            if cycle not in cycles:
                cycles[cycle] = []
            cycles[cycle].append({
                "tool": query["tool"],
                "params": query["params"]
            })
        
        # Find the most common sequence
        if cycles:
            # Get the most recent successful cycle
            recent_cycle = max(cycles.keys())
            sequences = cycles[recent_cycle]
        
        return sequences
    
    def _generate_query_id(self, tool_name: str, params: Dict) -> str:
        """Generate unique ID for a query"""
        content = f"{tool_name}_{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()[:8]
    
    def _summarize_result(self, result: Any) -> Dict:
        """Create a summary of the result for tracking"""
        if isinstance(result, dict):
            return {
                "type": "dict",
                "keys": list(result.keys())[:5],  # First 5 keys
                "size": len(result)
            }
        elif isinstance(result, list):
            return {
                "type": "list",
                "length": len(result),
                "sample": result[0] if result else None
            }
        elif isinstance(result, str):
            return {
                "type": "string",
                "length": len(result),
                "preview": result[:100]
            }
        else:
            return {
                "type": type(result).__name__,
                "value": str(result)[:100]
            }
    
    def _save_data(self):
        """Save query data to disk"""
        # Keep only last 100 successful queries
        if len(self.successful_queries) > 100:
            self.successful_queries = self.successful_queries[-100:]
        
        with open(self.successful_queries_file, 'w') as f:
            json.dump(self.successful_queries, f, indent=2)
        
        with open(self.query_patterns_file, 'w') as f:
            json.dump(self.query_patterns, f, indent=2)
    
    def generate_query_report(self) -> str:
        """Generate a report of successful query patterns"""
        report = "MCP Query Patterns Report\n"
        report += "=" * 50 + "\n\n"
        
        # Summary stats
        report += f"Total successful queries tracked: {len(self.successful_queries)}\n"
        report += f"Unique patterns identified: {len(self.query_patterns)}\n\n"
        
        # Pattern details
        report += "Successful Query Patterns:\n"
        report += "-" * 30 + "\n"
        
        for pattern_key, pattern in self.query_patterns.items():
            report += f"\nGoal Type: {pattern['goal_type']}\n"
            report += f"Tool: {pattern['tool']}\n"
            report += f"Usage Count: {pattern['usage_count']}\n"
            report += f"Recent Successful Parameters:\n"
            
            for i, param_set in enumerate(pattern["successful_params"][-3:], 1):
                report += f"  {i}. {json.dumps(param_set['params'], indent=4)}\n"
        
        return report
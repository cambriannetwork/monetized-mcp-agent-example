"""
Simple Setup for Cambrian Trading Agent
Single optional input for initial direction
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional


class SetupWizard:
    """Simple setup for first-time users"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self.knowledge_dir = Path("knowledge")
        self.user_config_file = self.config_dir / "user_config.json"
        
    def print_welcome(self):
        """Display welcome message"""
        print("""
╔════════════════════════════════════════════════════════════╗
║          Welcome to Cambrian Trading Agent!                ║
║                                                            ║
║  You can provide an optional direction for the agent,      ║
║  or press Enter to use the default configuration.          ║
╚════════════════════════════════════════════════════════════╝
        """)
    
    def reset_project(self, confirm: bool = True):
        """Reset the project to fresh state"""
        if confirm:
            response = input("\n⚠️  This will delete all existing data and configurations. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Reset cancelled.")
                return False
        
        print("\n🔄 Resetting project...")
        
        # Backup existing data
        backup_dir = Path(f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Directories to reset
        dirs_to_reset = [
            "knowledge/research/findings",
            "knowledge/goals", 
            "knowledge/mcp_queries",
            "models"
        ]
        
        for dir_path in dirs_to_reset:
            path = Path(dir_path)
            if path.exists():
                # Backup
                backup_path = backup_dir / dir_path
                backup_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copytree(path, backup_path)
                
                # Clear
                shutil.rmtree(path)
                path.mkdir(parents=True, exist_ok=True)
                print(f"  ✓ Reset {dir_path}")
        
        # Reset state file
        state_file = Path("knowledge/state.json")
        if state_file.exists():
            shutil.copy(state_file, backup_dir / "state.json")
            state_file.write_text(json.dumps({"cycle_count": 0}, indent=2))
        
        print(f"\n✅ Reset complete. Backup saved to: {backup_dir}")
        return True
    
    async def run_interactive_setup(self) -> Dict:
        """Run the simple setup process"""
        self.print_welcome()
        
        # Get optional direction
        print("\n📝 Optional: Provide a direction for your agent")
        print("Examples:")
        print("  - 'Focus on arbitrage opportunities'")
        print("  - 'Conservative risk, long-term holds'")
        print("  - 'Research momentum trading strategies'")
        print("  - Press Enter for default configuration")
        
        user_direction = input("\nYour direction (optional): ").strip()
        
        # Create config based on direction
        config = self._create_config_from_direction(user_direction)
        
        # Generate goals based on direction
        goals = self._generate_goals_from_direction(user_direction)
        
        # Save configurations
        self._save_config(config)
        self._save_goals(goals)
        
        print("\n✅ Setup Complete!")
        if user_direction:
            print(f"Direction: {user_direction}")
        else:
            print("Using default configuration")
        
        return config
    
    def _create_config_from_direction(self, direction: str) -> Dict:
        """Create configuration based on user direction"""
        # Default config
        config = {
            "created_at": datetime.now().isoformat(),
            "version": "1.0",
            "user_direction": direction if direction else "default",
            "objectives": {
                "primary": "market_research",
                "selected": ["market_research", "profit_maximization"],
                "time_horizon": "days"
            },
            "risk_profile": {
                "tolerance": "moderate",
                "max_position_pct": 10.0,
                "stop_loss_pct": 5.0,
                "use_leverage": False
            },
            "agent": {
                "cycle_interval_seconds": 15,  # 15 seconds default
                "auto_purchase": True,
                "daily_budget_usdc": 0.1,
                "max_concurrent_research": 3
            }
        }
        
        # Adjust based on direction keywords
        if direction:
            direction_lower = direction.lower()
            
            # Arbitrage focus
            if "arbitrage" in direction_lower:
                config["objectives"]["primary"] = "arbitrage"
                config["objectives"]["selected"] = ["arbitrage", "market_research"]
                config["agent"]["cycle_interval_seconds"] = 15  # Fast for arbitrage
            
            # Conservative
            elif "conservative" in direction_lower or "risk" in direction_lower:
                config["risk_profile"]["tolerance"] = "conservative"
                config["risk_profile"]["max_position_pct"] = 5.0
                config["agent"]["cycle_interval_seconds"] = 30  # 30 seconds for conservative
            
            # Momentum/aggressive
            elif "momentum" in direction_lower or "aggressive" in direction_lower:
                config["objectives"]["primary"] = "trend_following"
                config["risk_profile"]["tolerance"] = "aggressive"
                config["risk_profile"]["max_position_pct"] = 20.0
                config["agent"]["cycle_interval_seconds"] = 15  # 15 seconds for momentum
            
            # Research focus
            elif "research" in direction_lower:
                config["objectives"]["primary"] = "market_research"
                config["agent"]["auto_purchase"] = True
                config["agent"]["daily_budget_usdc"] = 0.2  # More budget for research
        
        return config
    
    def _generate_goals_from_direction(self, direction: str) -> List[Dict]:
        """Generate initial goals based on direction"""
        goals = []
        
        # Always include market analysis
        goals.append({
            "id": "goal_001",
            "title": "SOL Price Trend Analysis",
            "description": "Track and analyze SOL price movements and identify trends",
            "status": "active",
            "priority": "high",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "metrics": ["price_accuracy", "trend_detection"]
        })
        
        # Add direction-specific goals
        if direction:
            direction_lower = direction.lower()
            
            if "arbitrage" in direction_lower:
                goals.append({
                    "id": "goal_002",
                    "title": "Cross-DEX Arbitrage Opportunities",
                    "description": "Identify price discrepancies between different DEXs",
                    "status": "active",
                    "priority": "high",
                    "created_at": datetime.now().isoformat(),
                    "progress": 0,
                    "metrics": ["opportunities_found", "profit_potential"]
                })
            
            elif "momentum" in direction_lower or "trend" in direction_lower:
                goals.append({
                    "id": "goal_002",
                    "title": "Momentum Trading Signals",
                    "description": "Develop momentum-based entry and exit signals",
                    "status": "active",
                    "priority": "high",
                    "created_at": datetime.now().isoformat(),
                    "progress": 0,
                    "metrics": ["signal_accuracy", "profit_factor"]
                })
            
            elif "conservative" in direction_lower or "long" in direction_lower:
                goals.append({
                    "id": "goal_002",
                    "title": "Long-term Value Analysis",
                    "description": "Identify tokens with strong fundamentals for long-term holding",
                    "status": "active",
                    "priority": "medium",
                    "created_at": datetime.now().isoformat(),
                    "progress": 0,
                    "metrics": ["fundamental_score", "risk_assessment"]
                })
        
        # Default additional goal
        goals.append({
            "id": f"goal_{len(goals)+1:03d}",
            "title": "Market Volatility Research",
            "description": "Analyze volatility patterns to optimize entry and exit timing",
            "status": "active",
            "priority": "medium",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "metrics": ["volatility_prediction", "timing_accuracy"]
        })
        
        return goals
    
    def _save_config(self, config: Dict):
        """Save user configuration"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        with open(self.user_config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _save_goals(self, goals: List[Dict]):
        """Save initial goals"""
        goals_dir = Path("knowledge/goals")
        goals_dir.mkdir(parents=True, exist_ok=True)
        
        goals_data = {"goals": goals}
        
        with open(goals_dir / "goals.json", 'w') as f:
            json.dump(goals_data, f, indent=2)
    
    def check_first_run(self) -> bool:
        """Check if this is the first run"""
        return not self.user_config_file.exists()
    
    def load_config(self) -> Optional[Dict]:
        """Load existing configuration"""
        if self.user_config_file.exists():
            with open(self.user_config_file) as f:
                return json.load(f)
        return None


# Standalone setup function
async def run_setup(reset: bool = False):
    """Run the setup wizard"""
    wizard = SetupWizard()
    
    if reset:
        if not wizard.reset_project():
            return None
    
    config = await wizard.run_interactive_setup()
    return config
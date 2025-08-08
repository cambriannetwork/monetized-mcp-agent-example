"""
Goal management system for the agent
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field

import structlog

logger = structlog.get_logger()


@dataclass
class Goal:
    """Represents a research or trading goal"""
    id: str
    title: str
    description: str
    priority: str  # high, medium, low
    status: str  # not_started, in_progress, completed
    created_at: str
    updated_at: str
    metrics: Dict = field(default_factory=dict)
    findings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metrics': self.metrics,
            'findings': self.findings
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Goal':
        return cls(**data)


class GoalManager:
    """Manages agent goals and priorities"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.goals_path = Path("knowledge/goals")
        self.goals: List[Goal] = []
    
    async def load_goals(self):
        """Load goals from JSON file"""
        goals_file = self.goals_path / "goals.json"
        
        if not goals_file.exists():
            logger.warning("No goals file found, creating default goals")
            self.goals = []
            return
        
        try:
            # Load goals from JSON
            with open(goals_file, 'r') as f:
                data = json.load(f)
                
            self.goals = []
            for goal_data in data.get('goals', []):
                # Convert the goal format from Claude's output
                goal = Goal(
                    id=goal_data.get('id', ''),
                    title=goal_data.get('title', ''),
                    description=goal_data.get('description', ''),
                    priority=goal_data.get('priority', 'medium'),
                    status=goal_data.get('status', 'active'),
                    created_at=goal_data.get('created_at', datetime.now().isoformat()),
                    updated_at=goal_data.get('updated_at', datetime.now().isoformat()),
                    metrics=goal_data.get('metrics', {}),
                    findings=goal_data.get('findings', [])
                )
                self.goals.append(goal)
            
            logger.info(f"Loaded {len(self.goals)} goals from JSON")
        except Exception as e:
            logger.error(f"Error loading goals: {e}")
            self.goals = []
    
    async def get_active_goals(self) -> List[Goal]:
        """Get goals that are not completed, sorted by priority"""
        active = [g for g in self.goals if g.status != "completed"]
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        active.sort(key=lambda g: priority_order.get(g.priority, 999))
        
        return active
    
    async def update_goal(self, goal_id: str, updates: Dict):
        """Update a goal's status or findings"""
        for goal in self.goals:
            if goal.id == goal_id:
                for key, value in updates.items():
                    if hasattr(goal, key):
                        setattr(goal, key, value)
                goal.updated_at = datetime.now().isoformat()
                
                logger.info(f"Updated goal {goal_id}", updates=updates)
                await self._save_goals()
                return goal
        
        logger.warning(f"Goal {goal_id} not found")
        return None
    
    async def add_finding(self, goal_id: str, finding: str):
        """Add a finding to a goal"""
        for goal in self.goals:
            if goal.id == goal_id:
                goal.findings.append({
                    'timestamp': datetime.now().isoformat(),
                    'finding': finding
                })
                goal.updated_at = datetime.now().isoformat()
                
                # Save finding to file
                finding_file = Path(f"knowledge/research/findings/{goal_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md")
                finding_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(finding_file, 'w') as f:
                    f.write(f"# Finding for {goal.title}\n\n")
                    f.write(f"**Date**: {datetime.now().isoformat()}\n\n")
                    f.write(f"**Goal**: {goal.title}\n\n")
                    f.write(f"## Finding\n\n{finding}\n")
                
                logger.info(f"Added finding to goal {goal_id}")
                await self._save_goals()
                return
        
        logger.warning(f"Goal {goal_id} not found")
    
    async def _create_default_goals(self):
        """Create default goals file"""
        # Goals are already defined in current_goals.md
        pass
    
    async def _save_goals(self):
        """Save goals state to JSON"""
        state_file = self.goals_path / "goals_state.json"
        
        with open(state_file, 'w') as f:
            json.dump({
                'goals': [g.to_dict() for g in self.goals],
                'last_updated': datetime.now().isoformat()
            }, f, indent=2)
        
        logger.info("Saved goals state")
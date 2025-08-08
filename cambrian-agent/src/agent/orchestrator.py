"""
Orchestrator for coordinating agent activities
"""

import asyncio
from typing import Dict, List, Optional
from datetime import datetime

import structlog

logger = structlog.get_logger()


class Orchestrator:
    """Coordinates different agent modules and activities"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.active_tasks = []
        self.task_history = []
    
    async def plan_next_actions(self, goals: List, market_state: Optional[Dict] = None) -> List[Dict]:
        """Plan next actions based on goals and market state"""
        actions = []
        
        for goal in goals[:self.config['agent']['max_concurrent_research']]:
            if goal.status == "not_started":
                actions.append({
                    'type': 'research',
                    'goal_id': goal.id,
                    'action': 'initialize',
                    'priority': goal.priority
                })
            elif goal.status == "in_progress":
                actions.append({
                    'type': 'continue',
                    'goal_id': goal.id,
                    'action': 'analyze',
                    'priority': goal.priority
                })
        
        logger.info(f"Planned {len(actions)} actions")
        return actions
    
    async def execute_action(self, action: Dict) -> Dict:
        """Execute a planned action"""
        logger.info(f"Executing action", action_type=action['type'], goal_id=action.get('goal_id'))
        
        result = {
            'action': action,
            'status': 'pending',
            'started_at': datetime.now().isoformat()
        }
        
        try:
            if action['type'] == 'research':
                result['outcome'] = await self._execute_research(action)
            elif action['type'] == 'continue':
                result['outcome'] = await self._continue_analysis(action)
            else:
                result['outcome'] = {'error': f"Unknown action type: {action['type']}"}
            
            result['status'] = 'completed'
        except Exception as e:
            logger.error(f"Action execution failed", error=str(e), action=action)
            result['status'] = 'failed'
            result['error'] = str(e)
        
        result['completed_at'] = datetime.now().isoformat()
        self.task_history.append(result)
        
        return result
    
    async def _execute_research(self, action: Dict) -> Dict:
        """Execute research action"""
        return {
            'type': 'research_initialized',
            'goal_id': action['goal_id'],
            'next_steps': ['gather_data', 'analyze_patterns', 'document_findings']
        }
    
    async def _continue_analysis(self, action: Dict) -> Dict:
        """Continue ongoing analysis"""
        return {
            'type': 'analysis_continued',
            'goal_id': action['goal_id'],
            'progress': 'ongoing'
        }
    
    def get_task_summary(self) -> Dict:
        """Get summary of executed tasks"""
        if not self.task_history:
            return {'total_tasks': 0}
        
        completed = [t for t in self.task_history if t['status'] == 'completed']
        failed = [t for t in self.task_history if t['status'] == 'failed']
        
        return {
            'total_tasks': len(self.task_history),
            'completed': len(completed),
            'failed': len(failed),
            'success_rate': len(completed) / len(self.task_history) if self.task_history else 0,
            'last_task': self.task_history[-1] if self.task_history else None
        }
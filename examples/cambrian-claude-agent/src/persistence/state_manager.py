"""
State management for agent persistence
"""

import json
import aiofiles
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

import structlog

logger = structlog.get_logger()


class StateManager:
    """Manages agent state persistence"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.state_file = Path(config['persistence']['state_file'])
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state: Dict = {}
    
    async def load_state(self) -> Optional[Dict]:
        """Load state from file"""
        if not self.state_file.exists():
            logger.info("No previous state found")
            return None
        
        try:
            async with aiofiles.open(self.state_file, 'r') as f:
                content = await f.read()
                self.state = json.loads(content)
                logger.info("Loaded previous state", 
                           last_run=self.state.get('last_run'),
                           cycle_count=self.state.get('cycle_count', 0))
                return self.state
        except Exception as e:
            logger.error(f"Failed to load state", error=str(e))
            return None
    
    async def save_state(self, updates: Dict):
        """Save state to file"""
        self.state.update(updates)
        self.state['last_saved'] = datetime.now().isoformat()
        
        try:
            async with aiofiles.open(self.state_file, 'w') as f:
                await f.write(json.dumps(self.state, indent=2))
            logger.info("State saved successfully")
        except Exception as e:
            logger.error(f"Failed to save state", error=str(e))
    
    async def checkpoint(self, checkpoint_data: Dict):
        """Create a checkpoint of current progress"""
        checkpoint_dir = self.state_file.parent / "checkpoints"
        checkpoint_dir.mkdir(exist_ok=True)
        
        checkpoint_file = checkpoint_dir / f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'state': self.state.copy(),
            'checkpoint_data': checkpoint_data
        }
        
        try:
            async with aiofiles.open(checkpoint_file, 'w') as f:
                await f.write(json.dumps(checkpoint, indent=2))
            logger.info(f"Checkpoint created", file=checkpoint_file.name)
        except Exception as e:
            logger.error(f"Failed to create checkpoint", error=str(e))
    
    def get_state(self) -> Dict:
        """Get current state"""
        return self.state.copy()
    
    def update_metric(self, metric_name: str, value: any):
        """Update a specific metric in state"""
        if 'metrics' not in self.state:
            self.state['metrics'] = {}
        
        self.state['metrics'][metric_name] = {
            'value': value,
            'updated_at': datetime.now().isoformat()
        }
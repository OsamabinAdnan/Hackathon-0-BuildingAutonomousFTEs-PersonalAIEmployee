"""
Task Tracker - Ralph Wiggum Loop

Tracks task completion state for autonomous multi-step tasks.

Usage:
    tracker = TaskTracker()
    tracker.start_task("process-inbox")
    tracker.mark_step_complete("move-to-in-progress", "file1.md")
    tracker.mark_task_complete()
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from enum import Enum

logger = logging.getLogger('ralph_wiggum.tracker')


class TaskState(Enum):
    """Task states."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"


class TaskTracker:
    """
    Tracks task completion state for Ralph Wiggum loop.
    
    Monitors:
    - Task start/end
    - Steps completed
    - Files processed
    - Iteration count
    - Completion status
    """
    
    def __init__(self, vault_path: str = './AI_Employee_Vault_FTE'):
        """
        Initialize task tracker.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.tracker_file = self.vault_path / 'Logs' / 'ralph_wiggum_state.json'
        
        # Ensure logs directory exists
        self.tracker_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load or initialize state
        self.state = self._load_state()
    
    def _load_state(self) -> dict:
        """Load state from file or initialize new."""
        if self.tracker_file.exists():
            try:
                with open(self.tracker_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load state: {e}")
        
        return self._initialize_state()
    
    def _initialize_state(self) -> dict:
        """Initialize new state."""
        state = {
            'current_task': None,
            'task_state': TaskState.PENDING.value,
            'iteration': 0,
            'max_iterations': 10,
            'started_at': None,
            'completed_at': None,
            'steps': [],
            'files_processed': [],
            'errors': [],
            'completion_signals': []
        }
        self._save_state(state)
        return state
    
    def _save_state(self, state: dict = None):
        """Save state to file."""
        if state:
            self.state = state
        
        with open(self.tracker_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    def start_task(self, task_name: str, max_iterations: int = 10):
        """
        Start tracking a new task.
        
        Args:
            task_name: Name of the task
            max_iterations: Maximum iterations allowed
        """
        self.state = self._initialize_state()
        self.state['current_task'] = task_name
        self.state['task_state'] = TaskState.IN_PROGRESS.value
        self.state['max_iterations'] = max_iterations
        self.state['started_at'] = datetime.now().isoformat()
        self.state['iteration'] = 1
        
        self._save_state()
        logger.info(f"Task started: {task_name} (max {max_iterations} iterations)")
    
    def increment_iteration(self) -> int:
        """
        Increment iteration counter.
        
        Returns:
            New iteration number
        """
        self.state['iteration'] += 1
        iteration = self.state['iteration']
        
        if iteration > self.state['max_iterations']:
            self.state['task_state'] = TaskState.MAX_ITERATIONS.value
            logger.warning(f"Max iterations ({self.state['max_iterations']}) reached")
        
        self._save_state()
        return iteration
    
    def get_iteration(self) -> int:
        """Get current iteration number."""
        return self.state['iteration']
    
    def should_continue(self) -> bool:
        """
        Check if task should continue.
        
        Returns:
            True if under max iterations and not completed
        """
        return (
            self.state['iteration'] <= self.state['max_iterations'] and
            self.state['task_state'] not in [
                TaskState.COMPLETED.value,
                TaskState.FAILED.value
            ]
        )
    
    def mark_step_complete(self, step_name: str, details: str = None):
        """
        Mark a step as complete.
        
        Args:
            step_name: Name of the step
            details: Optional details about the step
        """
        step = {
            'name': step_name,
            'completed_at': datetime.now().isoformat(),
            'details': details
        }
        self.state['steps'].append(step)
        self._save_state()
        logger.debug(f"Step completed: {step_name}")
    
    def mark_file_processed(self, file_name: str, action: str = None):
        """
        Mark a file as processed.
        
        Args:
            file_name: Name of the file
            action: Action taken (moved, processed, etc.)
        """
        self.state['files_processed'].append({
            'name': file_name,
            'action': action,
            'processed_at': datetime.now().isoformat()
        })
        self._save_state()
    
    def mark_error(self, error: str, step: str = None):
        """
        Record an error.
        
        Args:
            error: Error message
            step: Step where error occurred
        """
        self.state['errors'].append({
            'error': error,
            'step': step,
            'occurred_at': datetime.now().isoformat()
        })
        self._save_state()
        logger.error(f"Error in {step or 'task'}: {error}")
    
    def add_completion_signal(self, signal: str):
        """
        Add a completion signal (e.g., "TASK_COMPLETE" tag found).
        
        Args:
            signal: Completion signal
        """
        self.state['completion_signals'].append({
            'signal': signal,
            'detected_at': datetime.now().isoformat()
        })
        self._save_state()
    
    def mark_task_complete(self):
        """Mark task as completed."""
        self.state['task_state'] = TaskState.COMPLETED.value
        self.state['completed_at'] = datetime.now().isoformat()
        self._save_state()
        logger.info(f"Task completed: {self.state['current_task']}")
    
    def mark_task_failed(self, reason: str):
        """
        Mark task as failed.
        
        Args:
            reason: Reason for failure
        """
        self.state['task_state'] = TaskState.FAILED.value
        self.state['completed_at'] = datetime.now().isoformat()
        self.state['errors'].append({
            'error': reason,
            'step': 'task',
            'occurred_at': datetime.now().isoformat()
        })
        self._save_state()
        logger.error(f"Task failed: {reason}")
    
    def get_state(self) -> dict:
        """Get current task state."""
        return self.state.copy()
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get task summary.
        
        Returns:
            Summary dict with key metrics
        """
        return {
            'task': self.state['current_task'],
            'state': self.state['task_state'],
            'iteration': self.state['iteration'],
            'max_iterations': self.state['max_iterations'],
            'steps_completed': len(self.state['steps']),
            'files_processed': len(self.state['files_processed']),
            'errors': len(self.state['errors']),
            'started_at': self.state['started_at'],
            'completed_at': self.state['completed_at']
        }
    
    def reset(self):
        """Reset tracker state."""
        self.state = self._initialize_state()
        logger.info("Task tracker reset")


# Global task tracker instance
_tracker = None


def get_task_tracker(vault_path: str = './AI_Employee_Vault_FTE') -> TaskTracker:
    """
    Get or create global task tracker instance.
    
    Args:
        vault_path: Path to Obsidian vault
    
    Returns:
        TaskTracker instance
    """
    global _tracker
    if _tracker is None:
        _tracker = TaskTracker(vault_path)
    return _tracker

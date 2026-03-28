"""
Ralph Wiggum Loop - Gold Tier

Autonomous multi-step task completion using stop hook pattern.

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

Usage:
    from ralph_wiggum import start_ralph_loop
    
    start_ralph_loop(
        prompt="Process all files in /Needs_Action, move to /Done when complete",
        max_iterations=10,
        vault_path="./AI_Employee_Vault_FTE"
    )
"""

from .stop_hook import StopHook, get_stop_hook
from .task_tracker import TaskTracker, get_task_tracker, TaskState

__all__ = [
    'StopHook',
    'get_stop_hook',
    'TaskTracker',
    'get_task_tracker',
    'TaskState',
    'start_ralph_loop',
]


def start_ralph_loop(
    prompt: str,
    max_iterations: int = 10,
    vault_path: str = './AI_Employee_Vault_FTE',
    completion_file: str = None
):
    """
    Start a Ralph Wiggum loop for autonomous task completion.
    
    Args:
        prompt: Task prompt for Claude
        max_iterations: Maximum retry attempts (default: 10)
        vault_path: Path to Obsidian vault
        completion_file: Optional file to monitor for completion
    """
    from .stop_hook import run_ralph_loop
    
    run_ralph_loop(
        prompt=prompt,
        max_iterations=max_iterations,
        vault_path=vault_path,
        completion_file=completion_file
    )

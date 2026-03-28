"""
Stop Hook - Ralph Wiggum Loop

Intercepts Claude's exit and re-injects prompt if task is incomplete.

Reference: https://github.com/anthropics/claude-code/tree/main/.claude/plugins/ralph-wiggum

Usage:
    from ralph_wiggum import StopHook
    
    hook = StopHook()
    hook.check_and_reinject(prompt, max_iterations=10)
"""

import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Optional

from .task_tracker import TaskTracker, TaskState, get_task_tracker

logger = logging.getLogger('ralph_wiggum.stop_hook')


class StopHook:
    """
    Stop hook for Ralph Wiggum loop.
    
    Intercepts Claude's exit and:
    1. Checks if task is complete
    2. If not complete and under max iterations, re-injects prompt
    3. If complete or max iterations, allows exit
    """
    
    def __init__(self, vault_path: str = './AI_Employee_Vault_FTE'):
        """
        Initialize stop hook.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path)
        self.tracker = get_task_tracker(str(vault_path))
    
    def check_completion(self, completion_file: str = None) -> bool:
        """
        Check if task is complete.
        
        Checks for:
        1. Completion signals in tracker
        2. File movement (from /Needs_Action/ to /Done/)
        3. Completion file existence (if provided)
        
        Args:
            completion_file: Optional file to check for completion
        
        Returns:
            True if task is complete
        """
        # Check tracker for completion signals
        state = self.tracker.get_state()
        
        if state['completion_signals']:
            logger.info(f"Completion signal detected: {state['completion_signals'][-1]['signal']}")
            return True
        
        # Check if completion file exists
        if completion_file:
            completion_path = Path(completion_file)
            if completion_path.exists():
                logger.info(f"Completion file exists: {completion_file}")
                return True
        
        # Check if files were moved to /Done/
        done_folder = self.vault_path / 'Done'
        if done_folder.exists():
            # If files were processed and moved to Done, task might be complete
            processed_count = len(state['files_processed'])
            if processed_count > 0:
                logger.info(f"{processed_count} files processed")
                # This is a heuristic - might need more sophisticated check
                return processed_count > 0
        
        return False
    
    def reinject_prompt(self, prompt: str) -> bool:
        """
        Re-inject prompt to Claude.
        
        Args:
            prompt: Prompt to re-inject
        
        Returns:
            True if successful
        """
        iteration = self.tracker.increment_iteration()
        
        logger.info(f"Re-injecting prompt (iteration {iteration})")
        
        # Log the re-injection
        self.tracker.mark_step_complete(
            'reinject_prompt',
            f'Iteration {iteration}'
        )
        
        # In a real implementation, this would interface with Claude's plugin system
        # For now, we'll just return True to indicate the prompt should be re-injected
        return True
    
    def check_and_reinject(
        self,
        prompt: str,
        completion_file: str = None
    ) -> bool:
        """
        Check if task is complete, re-inject if not.
        
        Args:
            prompt: Original prompt
            completion_file: Optional completion file to check
        
        Returns:
            True if re-injecting, False if task is complete
        """
        # Check if we should continue
        if not self.tracker.should_continue():
            state = self.tracker.get_state()
            logger.warning(f"Stopping: {state['task_state']}")
            return False
        
        # Check if task is complete
        if self.check_completion(completion_file):
            self.tracker.mark_task_complete()
            logger.info("Task complete, allowing exit")
            return False
        
        # Task not complete, re-inject prompt
        self.reinject_prompt(prompt)
        return True


def run_ralph_loop(
    prompt: str,
    max_iterations: int = 10,
    vault_path: str = './AI_Employee_Vault_FTE',
    completion_file: str = None
):
    """
    Run a Ralph Wiggum loop.
    
    This is a standalone function that runs Claude in a loop until:
    - Task is complete
    - Max iterations reached
    - User interrupts
    
    Args:
        prompt: Task prompt
        max_iterations: Maximum iterations (default: 10)
        vault_path: Path to Obsidian vault
        completion_file: Optional file to monitor for completion
    """
    tracker = get_task_tracker(vault_path)
    hook = StopHook(vault_path)
    
    # Start tracking
    tracker.start_task('ralph_loop', max_iterations)
    
    logger.info("=" * 60)
    logger.info("RALPH WIGGUM LOOP STARTED")
    logger.info("=" * 60)
    logger.info(f"Task: {prompt[:100]}...")
    logger.info(f"Max iterations: {max_iterations}")
    logger.info("=" * 60)
    
    try:
        while tracker.should_continue():
            iteration = tracker.get_iteration()
            
            logger.info("-" * 60)
            logger.info(f"ITERATION {iteration}/{max_iterations}")
            logger.info("-" * 60)
            
            # Run Claude with prompt
            logger.info("Running Claude...")
            
            process = subprocess.Popen(
                ['claude', '--print', '--dangerously-skip-permissions', prompt],
                cwd=str(vault_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            # Stream output
            for line in process.stdout:
                line = line.rstrip()
                if line:
                    print(line)
                    
                    # Check for completion signals in output
                    if 'TASK_COMPLETE' in line or '[DONE]' in line.lower():
                        tracker.add_completion_signal(line.strip())
                    
                    # Track file movements
                    if '[MOVE]' in line.upper():
                        if '/Done/' in line:
                            # Extract filename
                            parts = line.split('/')
                            if parts:
                                filename = parts[-1].strip()
                                tracker.mark_file_processed(filename, 'moved_to_done')
            
            process.wait()
            
            # Check result
            if process.returncode == 0:
                logger.info("Claude completed successfully")
                
                # Check if task is complete
                if hook.check_completion(completion_file):
                    tracker.mark_task_complete()
                    logger.info("Task complete!")
                    break
            else:
                logger.error(f"Claude failed with code {process.returncode}")
                tracker.mark_error(f"Claude failed with code {process.returncode}")
            
            # Prepare for next iteration
            if tracker.should_continue():
                logger.info("Task not complete, preparing next iteration...")
                time.sleep(2)  # Brief pause before next iteration
            else:
                break
        
        # Final summary
        summary = tracker.get_summary()
        logger.info("=" * 60)
        logger.info("RALPH WIGGUM LOOP FINISHED")
        logger.info("=" * 60)
        logger.info(f"Final state: {summary['state']}")
        logger.info(f"Iterations: {summary['iteration']}")
        logger.info(f"Files processed: {summary['files_processed']}")
        logger.info(f"Errors: {summary['errors']}")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        tracker.mark_task_failed("User interrupted")
    
    except Exception as e:
        logger.error(f"Error in Ralph loop: {e}")
        tracker.mark_task_failed(str(e))


# Global stop hook instance
_stop_hook = None


def get_stop_hook(vault_path: str = './AI_Employee_Vault_FTE') -> StopHook:
    """
    Get or create global stop hook instance.
    
    Args:
        vault_path: Path to Obsidian vault
    
    Returns:
        StopHook instance
    """
    global _stop_hook
    if _stop_hook is None:
        _stop_hook = StopHook(vault_path)
    return _stop_hook

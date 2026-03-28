"""
Orchestrator package for AI Employee.

The orchestrator coordinates:
- FileSystem Watcher (monitors /Inbox)
- Action detection (monitors /Needs_Action)
- Claude Code triggering (processes items)
"""

from .main import Orchestrator

__all__ = ['Orchestrator']

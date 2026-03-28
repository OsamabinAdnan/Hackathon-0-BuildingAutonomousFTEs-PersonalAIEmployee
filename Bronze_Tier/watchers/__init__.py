"""
Watchers package for AI Employee.

This package contains watcher implementations that monitor various
sources and create action files in the Obsidian vault.

Available watchers:
- BaseWatcher: Abstract base class for all watchers
- FileSystemWatcher: Monitors a folder for new files
"""

from .base_watcher import BaseWatcher
from .filesystem_watcher import FileSystemWatcher

__all__ = ['BaseWatcher', 'FileSystemWatcher']

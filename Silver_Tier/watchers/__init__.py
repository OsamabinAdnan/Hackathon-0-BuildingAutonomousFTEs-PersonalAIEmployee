"""
Watchers package for AI Employee (Silver Tier).

This package contains watcher implementations that monitor various
sources and create action files in the Obsidian vault.

Available watchers:
- BaseWatcher: Abstract base class for all watchers
- FileSystemWatcher: Monitors /Inbox folder → /Needs_Action/files/
- GmailWatcher: Monitors Gmail API → /Needs_Action/email/
- WhatsAppWatcher: Monitors WhatsApp Web → /Needs_Action/whatsapp/
- LinkedInWatcher: Monitors LinkedIn API → /Needs_Action/linkedin/

Usage:
    python -m watchers                  # All watchers
    python -m watchers.filesystem       # FileSystem only
    python -m watchers.gmail            # Gmail only
    python -m watchers.whatsapp         # WhatsApp only
    python -m watchers.linkedin         # LinkedIn only
"""

from .base_watcher import BaseWatcher
from .filesystem_watcher import FileSystemWatcher

# Optional imports - may not be available if dependencies not installed
try:
    from .gmail_watcher import GmailWatcher
except ImportError:
    GmailWatcher = None

try:
    from .whatsapp_watcher import WhatsAppWatcher
except ImportError:
    WhatsAppWatcher = None

try:
    from .linkedin_watcher import LinkedInWatcher
except ImportError:
    LinkedInWatcher = None

__all__ = [
    'BaseWatcher',
    'FileSystemWatcher',
    'GmailWatcher',
    'WhatsAppWatcher',
    'LinkedInWatcher',
]

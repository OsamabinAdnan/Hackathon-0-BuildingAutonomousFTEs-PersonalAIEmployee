"""
Orchestrator package for AI Employee - Gold Tier.

The orchestrator coordinates:
- FileSystem Watcher (monitors /Inbox)
- Facebook Watcher (monitors Facebook messages/posts)
- Action detection (monitors /Needs_Action including Odoo)
- Claude Code triggering (processes items with Gold Tier skills)
- Odoo Accounting integration (Gold Tier)
- Facebook integration (Gold Tier)
"""

from .main import Orchestrator

__all__ = ['Orchestrator']

"""
MCP Server package for AI Employee (Silver Tier).

This package contains the MCP server and service modules for external actions.

Architecture:
    Primary: Claude Code → MCP Server → External Actions
    Fallback: Claude Code → Direct Executor → External Actions

Available services:
- EmailService: Send emails via Gmail API
- WhatsAppService: Send WhatsApp messages via Playwright
- LinkedInService: Post to LinkedIn and send messages

MCP Server Tools:
- send_email: Send email via Gmail
- send_whatsapp: Send WhatsApp message
- post_linkedin: Post to LinkedIn
- send_linkedin_message: Send LinkedIn message

Direct Executor (Fallback):
- DirectExecutor: Execute actions when MCP is unavailable

Usage:
    # Run MCP server
    python -m mcp_server

    # Use Direct Executor as fallback
    from mcp_server.direct_executor import DirectExecutor
    executor = DirectExecutor()
    await executor.send_email(to, subject, body)
"""

from .server import mcp, run_server
from .direct_executor import DirectExecutor

__all__ = ['mcp', 'run_server', 'DirectExecutor']

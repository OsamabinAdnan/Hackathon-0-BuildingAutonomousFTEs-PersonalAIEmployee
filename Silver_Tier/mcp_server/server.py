"""
MCP Server - FastMCP server for AI Employee external actions.

This server exposes tools for Claude Code to interact with external services:
- send_email: Send email via Gmail
- send_whatsapp: Send WhatsApp message
- post_linkedin: Post to LinkedIn
- send_linkedin_message: Send LinkedIn message

Usage:
    python -m mcp_server

Configuration:
    Set environment variables in .env file:
    - GMAIL_CREDENTIALS_PATH: Path to Gmail OAuth credentials
    - GMAIL_TOKEN_PATH: Path to store Gmail token
    - LINKEDIN_ACCESS_TOKEN: LinkedIn API access token
    - WHATSAPP_SESSION_PATH: Path for WhatsApp session storage
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional, List

from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp_server')

# Try to import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    logger.warning('MCP package not installed. Install with: pip install mcp')
    MCP_AVAILABLE = False
    FastMCP = None


# Initialize services lazily
_email_service = None
_whatsapp_service = None
_linkedin_service = None


def get_email_service():
    """Get or create email service."""
    global _email_service
    if _email_service is None:
        from .email_service import EmailService
        _email_service = EmailService()
    return _email_service


def get_whatsapp_service():
    """Get or create WhatsApp service."""
    global _whatsapp_service
    if _whatsapp_service is None:
        from .whatsapp_service import WhatsAppService
        _whatsapp_service = WhatsAppService()
    return _whatsapp_service


def get_linkedin_service():
    """Get or create LinkedIn service."""
    global _linkedin_service
    if _linkedin_service is None:
        from .linkedin_service import LinkedInService
        _linkedin_service = LinkedInService()
    return _linkedin_service


# Create FastMCP server
if MCP_AVAILABLE:
    mcp = FastMCP(
        name="AI Employee MCP Server"
        # FastMCP constructor only accepts name parameter, not version or description
    )

    # ========================================
    # Email Tools
    # ========================================

    @mcp.tool()
    async def send_email(
        to: str,
        subject: str,
        body: str,
        cc: Optional[str] = None,
        bcc: Optional[str] = None,
        html: bool = False
    ) -> str:
        """
        Send an email via Gmail.

        Args:
            to: Recipient email address
            subject: Email subject line
            body: Email body content (plain text or HTML)
            cc: Optional CC recipients (comma-separated)
            bcc: Optional BCC recipients (comma-separated)
            html: Whether body is HTML format

        Returns:
            Result message with success status
        """
        service = get_email_service()

        cc_list = [e.strip() for e in cc.split(',')] if cc else None
        bcc_list = [e.strip() for e in bcc.split(',')] if bcc else None

        result = await service.send_email(
            to=to,
            subject=subject,
            body=body,
            cc=cc_list,
            bcc=bcc_list,
            html=html
        )

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would send email to {to}"
            return f"Email sent successfully to {to} (Message ID: {result.get('message_id', 'N/A')})"
        else:
            return f"Failed to send email: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    async def create_email_draft(
        to: str,
        subject: str,
        body: str,
        html: bool = False
    ) -> str:
        """
        Create an email draft in Gmail.

        Args:
            to: Recipient email address
            subject: Email subject line
            body: Email body content
            html: Whether body is HTML format

        Returns:
            Result message with draft ID
        """
        service = get_email_service()

        result = await service.create_draft(
            to=to,
            subject=subject,
            body=body,
            html=html
        )

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would create draft to {to}"
            return f"Draft created successfully (Draft ID: {result.get('draft_id', 'N/A')})"
        else:
            return f"Failed to create draft: {result.get('error', 'Unknown error')}"

    # ========================================
    # WhatsApp Tools
    # ========================================

    @mcp.tool()
    async def send_whatsapp(
        contact: str,
        message: str
    ) -> str:
        """
        Send a WhatsApp message.

        Args:
            contact: Contact name or phone number
            message: Message text to send

        Returns:
            Result message with success status
        """
        service = get_whatsapp_service()

        result = service.send_message(contact=contact, message=message)

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would send WhatsApp to {contact}"
            return f"WhatsApp message sent to {contact}"
        else:
            return f"Failed to send WhatsApp: {result.get('error', 'Unknown error')}"

    # ========================================
    # LinkedIn Tools
    # ========================================

    @mcp.tool()
    async def post_linkedin(
        text: str,
        visibility: str = "PUBLIC"
    ) -> str:
        """
        Post to LinkedIn.

        Args:
            text: Post text content
            visibility: Post visibility - "PUBLIC" or "CONNECTIONS"

        Returns:
            Result message with post ID
        """
        service = get_linkedin_service()

        result = await service.post_share(text=text, visibility=visibility)

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would post to LinkedIn: {text[:50]}..."
            return f"LinkedIn post created successfully (Post ID: {result.get('post_id', 'N/A')})"
        else:
            return f"Failed to post to LinkedIn: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    async def post_linkedin_organization(
        text: str,
        visibility: str = "PUBLIC"
    ) -> str:
        """
        Post to LinkedIn on behalf of organization.

        Args:
            text: Post text content
            visibility: Post visibility - "PUBLIC" or "CONNECTIONS"

        Returns:
            Result message with post ID
        """
        service = get_linkedin_service()

        result = await service.post_organization_share(text=text, visibility=visibility)

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would post to LinkedIn organization"
            return f"LinkedIn organization post created successfully"
        else:
            return f"Failed to post: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    async def send_linkedin_message(
        user_urn: str,
        message: str,
        subject: Optional[str] = None
    ) -> str:
        """
        Send a LinkedIn message to a user.

        Args:
            user_urn: Recipient's LinkedIn URN (e.g., 'urn:li:person:xxx')
            message: Message text
            subject: Optional message subject

        Returns:
            Result message with success status
        """
        service = get_linkedin_service()

        result = await service.send_message(
            recipient_urn=user_urn,
            message=message,
            subject=subject
        )

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would send LinkedIn message to {user_urn}"
            return f"LinkedIn message sent to {user_urn}"
        else:
            return f"Failed to send message: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    async def get_linkedin_profile() -> str:
        """
        Get current user's LinkedIn profile information.

        Returns:
            Profile information as formatted string
        """
        service = get_linkedin_service()

        result = await service.get_profile()

        if result.get('success'):
            if result.get('dry_run'):
                return "[DRY RUN] Would get LinkedIn profile"
            profile = result.get('profile', {})
            return f"Profile: {profile.get('firstName', {}).get('localized', {}).get('en_US', 'N/A')} {profile.get('lastName', {}).get('localized', {}).get('en_US', 'N/A')}"
        else:
            return f"Failed to get profile: {result.get('error', 'Unknown error')}"

else:
    # MCP not available - create placeholder
    mcp = None
    logger.error("MCP package not available. Tools will not be registered.")


def run_server(transport: str = 'stdio', port: int = 8000):
    """
    Run the MCP server.

    Args:
        transport: Transport type ('stdio' or 'http')
        port: Port for HTTP transport
    """
    if not MCP_AVAILABLE:
        logger.error("MCP package not installed. Cannot run server.")
        logger.error("Install with: pip install mcp")
        sys.exit(1)

    logger.info(f"Starting MCP Server...")
    logger.info(f"Transport: {transport}")

    if transport == 'stdio':
        mcp.run(transport='stdio')
    else:
        mcp.run(transport='streamable-http')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='AI Employee MCP Server - External action tools'
    )
    parser.add_argument(
        '--transport',
        type=str,
        default='stdio',
        choices=['stdio', 'http'],
        help='Transport type (default: stdio)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for HTTP transport (default: 8000)'
    )

    args = parser.parse_args()

    run_server(transport=args.transport, port=args.port)


if __name__ == '__main__':
    main()

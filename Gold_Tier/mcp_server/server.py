"""
MCP Server - FastMCP server for AI Employee external actions (Gold Tier).

This server exposes tools for Claude Code to interact with external services:
- send_email: Send email via Gmail
- send_whatsapp: Send WhatsApp message
- post_linkedin: Post to LinkedIn
- send_linkedin_message: Send LinkedIn message
- create_invoice: Create invoice in Odoo
- record_payment: Record payment in Odoo
- get_financial_report: Get Odoo financial report
- list_unpaid_invoices: List unpaid Odoo invoices
- post_facebook: Post to Facebook Page
- send_facebook_message: Send Facebook message
- get_facebook_insights: Get Facebook Page insights

Usage:
    python -m mcp_server

Configuration:
    Set environment variables in .env file:
    - GMAIL_CREDENTIALS_PATH: Path to Gmail OAuth credentials
    - GMAIL_TOKEN_PATH: Path to store Gmail token
    - LINKEDIN_ACCESS_TOKEN: LinkedIn API access token
    - WHATSAPP_SESSION_PATH: Path for WhatsApp session storage
    - ODOO_URL: Odoo instance URL
    - ODOO_DB: Database name
    - ODOO_USERNAME: Odoo username
    - ODOO_PASSWORD: Odoo password
    - FACEBOOK_APP_ID: Facebook App ID
    - FACEBOOK_APP_SECRET: Facebook App Secret
    - FACEBOOK_ACCESS_TOKEN: Facebook Page Access Token
    - FACEBOOK_PAGE_ID: Facebook Page ID
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
_odoo_service = None
_facebook_service = None


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


def get_odoo_service():
    """Get or create Odoo service."""
    global _odoo_service
    if _odoo_service is None:
        from .odoo_service import OdooService
        _odoo_service = OdooService(vault_path='./AI_Employee_Vault_FTE')
    return _odoo_service


def get_facebook_service():
    """Get or create Facebook service."""
    global _facebook_service
    if _facebook_service is None:
        from .facebook_service import FacebookService
        _facebook_service = FacebookService()
    return _facebook_service


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

    # ========================================
    # Odoo Tools
    # ========================================

    @mcp.tool()
    async def create_invoice(
        partner_name: str,
        amount: float,
        due_date: Optional[str] = None,
        description: str = None
    ) -> str:
        """
        Create a customer invoice in Odoo.

        Args:
            partner_name: Customer name or email
            amount: Invoice amount (without tax)
            due_date: Due date (YYYY-MM-DD), default 30 days
            description: Invoice line description

        Returns:
            Result message with invoice ID
        """
        service = get_odoo_service()

        result = await service.create_invoice(
            partner_name=partner_name,
            amount=amount,
            due_date=due_date,
            description=description
        )

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would create invoice for {partner_name}: ${amount}"
            return f"Invoice created (ID: {result.get('invoice_id')}) for {partner_name}: ${amount}, Due: {result.get('due_date')}"
        else:
            return f"Failed to create invoice: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    async def record_payment(
        invoice_id: int,
        amount: float,
        payment_date: Optional[str] = None,
        reference: str = None
    ) -> str:
        """
        Record a payment for an invoice.

        Args:
            invoice_id: Odoo invoice ID
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD), default today
            reference: Payment reference/note

        Returns:
            Result message with payment status
        """
        service = get_odoo_service()

        result = await service.record_payment(
            invoice_id=invoice_id,
            amount=amount,
            payment_date=payment_date,
            reference=reference
        )

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would record payment ${amount} for invoice {invoice_id}"
            return f"Payment recorded (ID: {result.get('payment_id')}): ${amount} for invoice {invoice_id}"
        else:
            return f"Failed to record payment: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    async def get_financial_report(period: str = 'month') -> str:
        """
        Get financial report from Odoo.

        Args:
            period: 'week', 'month', 'quarter', 'year'

        Returns:
            Formatted financial report
        """
        service = get_odoo_service()

        result = await service.get_financial_report(period=period)

        if result.get('success'):
            if result.get('dry_run'):
                return "[DRY RUN] Would get financial report"
            report = result.get('report', {})
            return f"""Financial Report ({period}):
- Revenue: ${report.get('revenue', 0):,.2f}
- Expenses: ${report.get('expenses', 0):,.2f}
- Profit: ${report.get('profit', 0):,.2f}
- Total Invoices: {report.get('invoice_count', 0)}"""
        else:
            return f"Failed to get financial report: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    async def list_unpaid_invoices() -> str:
        """
        List all unpaid customer invoices.

        Returns:
            Formatted list of unpaid invoices
        """
        service = get_odoo_service()

        result = await service.list_unpaid_invoices()

        if result.get('success'):
            if result.get('dry_run'):
                return "[DRY RUN] Would list unpaid invoices"
            invoices = result.get('invoices', [])
            if not invoices:
                return "No unpaid invoices found."
            output = f"Unpaid Invoices ({result.get('count', 0)}):\n\n"
            for inv in invoices:
                output += f"- {inv.get('number')}: {inv.get('partner')} - ${inv.get('total'):,.2f} (Due: ${inv.get('due'):,.2f})\n"
            return output
        else:
            return f"Failed to list unpaid invoices: {result.get('error', 'Unknown error')}"

    # ========================================
    # Facebook Tools
    # ========================================

    @mcp.tool()
    async def post_facebook(
        message: str,
        image_url: Optional[str] = None,
        link: Optional[str] = None
    ) -> str:
        """
        Post to Facebook Page.

        Args:
            message: Post text content
            image_url: Optional image URL
            link: Optional link to share

        Returns:
            Result message with post ID
        """
        service = get_facebook_service()

        result = await service.post_facebook(
            message=message,
            image_url=image_url,
            link=link
        )

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would post to Facebook: {message[:50]}..."
            return f"Facebook post created (ID: {result.get('post_id')})"
        else:
            return f"Failed to post to Facebook: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    async def send_facebook_message(
        recipient_id: str,
        message: str
    ) -> str:
        """
        Send a message via Facebook Page Messenger.

        Args:
            recipient_id: Recipient's Facebook user ID
            message: Message text

        Returns:
            Result message with status
        """
        service = get_facebook_service()

        result = await service.send_facebook_message(
            recipient_id=recipient_id,
            message=message
        )

        if result.get('success'):
            if result.get('dry_run'):
                return f"[DRY RUN] Would send Facebook message to {recipient_id}"
            return f"Facebook message sent to {recipient_id}"
        else:
            return f"Failed to send Facebook message: {result.get('error', 'Unknown error')}"

    @mcp.tool()
    async def get_facebook_insights() -> str:
        """
        Get Facebook Page insights.

        Returns:
            Formatted insights data
        """
        service = get_facebook_service()

        result = await service.get_facebook_insights()

        if result.get('success'):
            if result.get('dry_run'):
                return "[DRY RUN] Would get Facebook insights"
            return f"Facebook insights retrieved for page {result.get('page_id')}"
        else:
            return f"Failed to get Facebook insights: {result.get('error', 'Unknown error')}"

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

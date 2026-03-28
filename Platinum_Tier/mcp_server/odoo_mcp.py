"""
Odoo MCP Server - MCP server for Odoo accounting operations.

This server exposes tools for Claude Code to interact with Odoo:
- create_invoice: Create customer invoice
- record_payment: Record payment for invoice
- get_financial_report: Get financial reports
- list_unpaid_invoices: List outstanding invoices

Usage:
    python -m mcp_server.odoo_mcp

Configuration:
    Set environment variables in .env file:
    - ODOO_URL: Odoo instance URL
    - ODOO_DB: Database name
    - ODOO_USERNAME: Odoo username
    - ODOO_PASSWORD: Odoo password
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('odoo_mcp')

# Try to import FastMCP
try:
    from mcp.server.fastmcp import FastMCP
    MCP_AVAILABLE = True
except ImportError:
    logger.warning('MCP package not installed. Install with: pip install mcp')
    MCP_AVAILABLE = False
    FastMCP = None


# Initialize Odoo service lazily
_odoo_service = None


def get_odoo_service():
    """Get or create Odoo service."""
    global _odoo_service
    if _odoo_service is None:
        from .odoo_service import OdooService
        _odoo_service = OdooService()
    return _odoo_service


# Create FastMCP server
if MCP_AVAILABLE:
    mcp = FastMCP(
        name="Odoo MCP Server"
    )

    # ========================================
    # Invoice Tools
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
            return f"Invoice created successfully (ID: {result.get('invoice_id')}) for {partner_name}: ${amount}, Due: {result.get('due_date')}"
        else:
            return f"Failed to create invoice: {result.get('error', 'Unknown error')}"

    # ========================================
    # Payment Tools
    # ========================================

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
            return f"Payment recorded successfully (ID: {result.get('payment_id')}): ${amount} for invoice {invoice_id}"
        else:
            return f"Failed to record payment: {result.get('error', 'Unknown error')}"

    # ========================================
    # Financial Reports
    # ========================================

    @mcp.tool()
    async def get_financial_report(
        period: str = 'month',
        report_type: str = 'profit_loss'
    ) -> str:
        """
        Get financial report from Odoo.

        Args:
            period: 'week', 'month', 'quarter', 'year'
            report_type: 'profit_loss', 'balance_sheet'

        Returns:
            Formatted financial report
        """
        service = get_odoo_service()

        result = await service.get_financial_report(
            period=period,
            report_type=report_type
        )

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
                output += f"- {inv.get('number')}: {inv.get('partner')} - ${inv.get('total'):,.2f} (Due: ${inv.get('due'):,.2f}, Date: {inv.get('due_date')})\n"
            return output
        else:
            return f"Failed to list unpaid invoices: {result.get('error', 'Unknown error')}"

    # ========================================
    # Partner Tools
    # ========================================

    @mcp.tool()
    async def get_odoo_profile() -> str:
        """
        Get current Odoo user profile.

        Returns:
            Profile information
        """
        service = get_odoo_service()

        result = await service.get_profile()

        if result.get('success'):
            if result.get('dry_run'):
                return "[DRY RUN] Would get Odoo profile"
            
            profile = result.get('profile', {})
            return f"Odoo Profile: {profile.get('name')} ({profile.get('email')}) - Company: {profile.get('company')}"
        else:
            return f"Failed to get profile: {result.get('error', 'Unknown error')}"

else:
    # MCP not available - create placeholder
    mcp = None
    logger.error("MCP package not available. Tools will not be registered.")


def run_server(transport: str = 'stdio', port: int = 8000):
    """
    Run the Odoo MCP server.

    Args:
        transport: Transport type ('stdio' or 'http')
        port: Port for HTTP transport
    """
    if not MCP_AVAILABLE:
        logger.error("MCP package not installed. Cannot run server.")
        logger.error("Install with: pip install mcp")
        sys.exit(1)

    logger.info(f"Starting Odoo MCP Server...")
    logger.info(f"Transport: {transport}")

    if transport == 'stdio':
        mcp.run(transport='stdio')
    else:
        mcp.run(transport='streamable-http')


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Odoo MCP Server - Accounting tools'
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

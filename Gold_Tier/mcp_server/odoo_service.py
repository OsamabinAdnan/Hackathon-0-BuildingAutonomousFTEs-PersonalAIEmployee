"""
Odoo Service - Connect to Odoo via XML-RPC/JSON-RPC.

This service provides accounting capabilities via Odoo APIs:
- Create invoices
- Record payments
- Get financial reports
- Manage partners (customers/vendors)

Usage:
    from mcp_server.odoo_service import OdooService
    
    service = OdooService(
        url="http://localhost:8069",
        db="odoo_db",
        username="admin@example.com",
        password="your_password"
    )
    
    # Create invoice
    result = await service.create_invoice(
        partner_name="Client ABC",
        amount=5000,
        due_date="2026-04-01"
    )
"""

import logging
import os
from typing import Optional, List, Dict, Any
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger('mcp_server.odoo')


class OdooService:
    """
    Odoo service using XML-RPC API.
    
    Provides accounting operations via Odoo.
    """

    def __init__(
        self,
        url: str = None,
        db: str = None,
        username: str = None,
        password: str = None,
        vault_path: str = './AI_Employee_Vault_FTE'
    ):
        """
        Initialize Odoo service.

        Args:
            url: Odoo URL (e.g., http://localhost:8069)
            db: Database name
            username: Odoo username (email)
            password: Odoo password
            vault_path: Path to vault (for audit logging)
        """
        self.vault_path = vault_path  # Store for audit logging
        self.url = url or os.getenv('ODOO_URL', 'http://localhost:8069')
        self.db = db or os.getenv('ODOO_DB', 'odoo_db')
        self.username = username or os.getenv('ODOO_USERNAME')
        self.password = password or os.getenv('ODOO_PASSWORD')
        
        self.uid = None  # User ID after authentication
        self.common = None
        self.models = None
        
        # Dry run mode
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
        
        logger.info(f'Odoo Service initialized')
        logger.info(f'  URL: {self.url}')
        logger.info(f'  Database: {self.db}')
        logger.info(f'  Username: {self.username or "Not set"}')
        logger.info(f'  Dry Run: {self.dry_run}')

    def _connect(self) -> bool:
        """
        Connect and authenticate to Odoo.

        Returns:
            True if successful
        """
        try:
            import xmlrpc.client
            
            # Connect to common endpoint (authentication)
            self.common = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/common'
            )
            
            # Authenticate
            self.uid = self.common.authenticate(
                self.db,
                self.username,
                self.password,
                {}
            )
            
            if not self.uid:
                logger.error('Odoo authentication failed')
                return False
            
            # Connect to models endpoint (operations)
            self.models = xmlrpc.client.ServerProxy(
                f'{self.url}/xmlrpc/2/object',
                use_builtin_types=True
            )
            
            logger.info(f'Odoo connected successfully (UID: {self.uid})')
            return True
            
        except Exception as e:
            logger.error(f'Odoo connection failed: {e}')
            return False

    def _ensure_connected(self) -> bool:
        """Ensure connected, reconnect if needed."""
        if self.uid is None:
            return self._connect()
        return True

    async def create_invoice(
        self,
        partner_name: str,
        amount: float,
        due_date: str = None,
        description: str = None,
        invoice_type: str = 'out_invoice'
    ) -> Dict[str, Any]:
        """
        Create a customer invoice.

        Args:
            partner_name: Customer name or email
            amount: Invoice amount (without tax)
            due_date: Due date (YYYY-MM-DD)
            description: Invoice line description
            invoice_type: 'out_invoice' (customer) or 'in_invoice' (vendor)

        Returns:
            Dict with invoice_id and status
        """
        # Import audit logger
        from audit.logger import get_audit_logger
        audit_logger = get_audit_logger(str(self.vault_path))
        
        if self.dry_run:
            logger.info(f'[DRY RUN] Would create invoice for {partner_name}: ${amount}')
            audit_logger.log_odoo_invoice(
                invoice_id='DRY_RUN',
                partner=partner_name,
                amount=amount,
                status='success',
                error=None
            )
            return {
                'success': True,
                'dry_run': True,
                'partner': partner_name,
                'amount': amount
            }

        if not self._ensure_connected():
            audit_logger.log_odoo_invoice(
                invoice_id='FAILED',
                partner=partner_name,
                amount=amount,
                status='error',
                error='Connection failed'
            )
            return {'success': False, 'error': 'Connection failed'}

        try:
            # Find or create partner
            partner_id = await self._find_or_create_partner(partner_name)
            if not partner_id:
                audit_logger.log_odoo_invoice(
                    invoice_id='FAILED',
                    partner=partner_name,
                    amount=amount,
                    status='error',
                    error=f'Partner not found: {partner_name}'
                )
                return {'success': False, 'error': f'Partner not found: {partner_name}'}

            # Set default due date (30 days)
            if not due_date:
                from datetime import timedelta
                due = datetime.now() + timedelta(days=30)
                due_date = due.strftime('%Y-%m-%d')

            # Create invoice
            invoice_vals = {
                'move_type': invoice_type,
                'partner_id': partner_id,
                'invoice_date': datetime.now().strftime('%Y-%m-%d'),
                'invoice_date_due': due_date,
                'invoice_line_ids': [(0, 0, {
                    'name': description or 'Service',
                    'quantity': 1,
                    'price_unit': amount,
                })]
            }

            invoice_id = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'account.move',
                'create',
                [invoice_vals]
            )

            logger.info(f'Invoice created: {invoice_id} for {partner_name}')
            
            # Log to audit
            audit_logger.log_odoo_invoice(
                invoice_id=str(invoice_id),
                partner=partner_name,
                amount=amount,
                status='success',
                error=None
            )
            
            return {
                'success': True,
                'invoice_id': invoice_id,
                'partner': partner_name,
                'amount': amount,
                'due_date': due_date
            }

        except Exception as e:
            logger.error(f'Failed to create invoice: {e}')
            audit_logger.log_odoo_invoice(
                invoice_id='ERROR',
                partner=partner_name,
                amount=amount,
                status='error',
                error=str(e)
            )
            return {'success': False, 'error': str(e)}

    async def record_payment(
        self,
        invoice_id: int,
        amount: float,
        payment_date: str = None,
        reference: str = None
    ) -> Dict[str, Any]:
        """
        Record a payment for an invoice.

        Args:
            invoice_id: Odoo invoice ID
            amount: Payment amount
            payment_date: Payment date (YYYY-MM-DD)
            reference: Payment reference/note

        Returns:
            Dict with payment status
        """
        # Import audit logger
        from audit.logger import get_audit_logger
        audit_logger = get_audit_logger(str(self.vault_path))
        
        if self.dry_run:
            logger.info(f'[DRY RUN] Would record payment ${amount} for invoice {invoice_id}')
            audit_logger.log_odoo_payment(
                payment_id='DRY_RUN',
                invoice_id=str(invoice_id),
                amount=amount,
                status='success',
                error=None
            )
            return {
                'success': True,
                'dry_run': True,
                'invoice_id': invoice_id,
                'amount': amount
            }

        if not self._ensure_connected():
            audit_logger.log_odoo_payment(
                payment_id='FAILED',
                invoice_id=str(invoice_id),
                amount=amount,
                status='error',
                error='Connection failed'
            )
            return {'success': False, 'error': 'Connection failed'}

        try:
            if not payment_date:
                payment_date = datetime.now().strftime('%Y-%m-%d')

            # Create payment register
            payment_vals = {
                'payment_type': 'inbound',
                'partner_type': 'customer',
                'partner_id': self.models.execute_kw(
                    self.db, self.uid, self.password,
                    'account.move', 'read', [[invoice_id]]
                )[0]['partner_id'][0],
                'amount': amount,
                'payment_date': payment_date,
                'reference': reference or f'Payment for invoice {invoice_id}',
            }

            payment_id = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'account.payment',
                'create',
                [payment_vals]
            )

            # Confirm payment
            self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'account.payment',
                'action_post',
                [[payment_id]]
            )

            logger.info(f'Payment recorded: {payment_id} for invoice {invoice_id}')
            
            # Log to audit
            audit_logger.log_odoo_payment(
                payment_id=str(payment_id),
                invoice_id=str(invoice_id),
                amount=amount,
                status='success',
                error=None
            )
            
            return {
                'success': True,
                'payment_id': payment_id,
                'invoice_id': invoice_id,
                'amount': amount
            }

        except Exception as e:
            logger.error(f'Failed to record payment: {e}')
            audit_logger.log_odoo_payment(
                payment_id='ERROR',
                invoice_id=str(invoice_id),
                amount=amount,
                status='error',
                error=str(e)
            )
            return {'success': False, 'error': str(e)}

    async def get_financial_report(
        self,
        period: str = 'month',
        report_type: str = 'profit_loss'
    ) -> Dict[str, Any]:
        """
        Get financial report from Odoo.
        Note: Requires Invoicing or Accounting module installed.

        Args:
            period: 'week', 'month', 'quarter', 'year'
            report_type: 'profit_loss', 'balance_sheet'

        Returns:
            Dict with financial data
        """
        if self.dry_run:
            return {
                'success': True,
                'dry_run': True,
                'report': {'revenue': 0, 'expenses': 0, 'profit': 0}
            }

        if not self._ensure_connected():
            return {'success': False, 'error': 'Connection failed'}

        try:
            # Try to get invoices (works with Invoicing module)
            domain = [('state', '=', 'posted')]
            
            invoices = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'account.move',
                'search_read',
                [domain],
                {'fields': ['amount_total', 'move_type', 'date']}
            )

            revenue = sum(
                inv['amount_total'] for inv in invoices 
                if inv['move_type'] in ('out_invoice', 'out_refund')
            )
            expenses = sum(
                inv['amount_total'] for inv in invoices 
                if inv['move_type'] in ('in_invoice', 'in_refund')
            )

            return {
                'success': True,
                'report': {
                    'revenue': revenue,
                    'expenses': expenses,
                    'profit': revenue - expenses,
                    'invoice_count': len(invoices)
                }
            }

        except Exception as e:
            # If accounting module not installed, return zeros
            error_msg = str(e)
            if "account.move" in error_msg or "doesn't exist" in error_msg:
                return {
                    'success': True,
                    'report': {
                        'revenue': 0,
                        'expenses': 0,
                        'profit': 0,
                        'invoice_count': 0,
                        'note': 'Accounting/Invoicing module not installed'
                    }
                }
            logger.error(f'Failed to get financial report: {e}')
            return {'success': False, 'error': str(e)}

    async def list_unpaid_invoices(self) -> Dict[str, Any]:
        """
        List all unpaid customer invoices.
        Note: Requires Invoicing or Accounting module installed.

        Returns:
            Dict with list of unpaid invoices
        """
        if self.dry_run:
            return {'success': True, 'dry_run': True, 'invoices': []}

        if not self._ensure_connected():
            return {'success': False, 'error': 'Connection failed'}

        try:
            domain = [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', '!=', 'paid')
            ]

            invoices = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'account.move',
                'search_read',
                [domain],
                {'fields': ['name', 'partner_id', 'amount_total', 'amount_residual', 'invoice_date_due']}
            )

            result = []
            for inv in invoices:
                result.append({
                    'id': inv['id'],
                    'number': inv['name'],
                    'partner': inv['partner_id'][1] if inv['partner_id'] else 'Unknown',
                    'total': inv['amount_total'],
                    'due': inv['amount_residual'],
                    'due_date': inv['invoice_date_due']
                })

            return {
                'success': True,
                'invoices': result,
                'count': len(result)
            }

        except Exception as e:
            # If accounting module not installed, return empty list
            error_msg = str(e)
            if "account.move" in error_msg or "doesn't exist" in error_msg:
                return {
                    'success': True,
                    'invoices': [],
                    'count': 0,
                    'note': 'Accounting/Invoicing module not installed'
                }
            logger.error(f'Failed to list unpaid invoices: {e}')
            return {'success': False, 'error': str(e)}

    async def _find_or_create_partner(self, name: str, email: str = None) -> Optional[int]:
        """Find existing partner or create new one."""
        try:
            # Try to find by name
            partner_ids = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'res.partner',
                'search',
                [[('name', '=', name)]]
            )

            if partner_ids:
                return partner_ids[0]

            # Create new partner
            partner_vals = {'name': name}
            if email:
                partner_vals['email'] = email

            new_id = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'res.partner',
                'create',
                [partner_vals]
            )

            logger.info(f'Created new partner: {name} (ID: {new_id})')
            return new_id

        except Exception as e:
            logger.error(f'Failed to find/create partner: {e}')
            return None

    async def get_profile(self) -> Dict[str, Any]:
        """Get current user profile."""
        if self.dry_run:
            return {'success': True, 'dry_run': True, 'profile': {}}

        if not self._ensure_connected():
            return {'success': False, 'error': 'Connection failed'}

        try:
            user = self.models.execute_kw(
                self.db,
                self.uid,
                self.password,
                'res.users',
                'read',
                [[self.uid]],
                {'fields': ['name', 'email', 'company_id']}
            )[0]

            return {
                'success': True,
                'profile': {
                    'name': user.get('name', ''),
                    'email': user.get('email', ''),
                    'company': user.get('company_id', [None, ''])[1] if user.get('company_id') else ''
                }
            }

        except Exception as e:
            logger.error(f'Failed to get profile: {e}')
            return {'success': False, 'error': str(e)}

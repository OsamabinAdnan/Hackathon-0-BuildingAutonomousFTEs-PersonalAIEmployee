"""
Audit Logger - Gold Tier

Comprehensive audit logging for all AI Employee actions.
Logs all transactions, actions, errors, and recovery attempts.

Usage:
    from audit.logger import AuditLogger
    
    logger = AuditLogger()
    logger.log_action('odoo_service', 'create_invoice', 'success', {'invoice_id': '123'})
"""

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from dotenv import load_dotenv

load_dotenv()


class AuditLogger:
    """
    Centralized audit logger for Gold Tier AI Employee.
    
    Logs all actions in JSON format for:
    - Compliance and auditing
    - Debugging and troubleshooting
    - Performance analysis
    - Error tracking
    """
    
    def __init__(self, vault_path: str = './AI_Employee_Vault_FTE'):
        """
        Initialize audit logger.
        
        Args:
            vault_path: Path to Obsidian vault for log storage
        """
        self.vault_path = Path(vault_path)
        self.logs_dir = self.vault_path / 'Logs' / 'audit'
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        # Log file for today
        self.log_file = self.logs_dir / f"audit_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Initialize log file if it doesn't exist
        if not self.log_file.exists():
            self._init_log_file()
        
        # Setup standard logging for real-time output
        self._setup_standard_logger()
        
        # Dry run mode
        self.dry_run = os.getenv('DRY_RUN', 'false').lower() == 'true'
    
    def _init_log_file(self):
        """Initialize log file with empty array."""
        self.log_file.write_text('[]', encoding='utf-8')
    
    def _setup_standard_logger(self):
        """Setup standard Python logger for real-time output."""
        self.std_logger = logging.getLogger('audit')
        self.std_logger.setLevel(logging.INFO)
        
        # Only add handler if not already added
        if not self.std_logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | [AUDIT] %(message)s',
                datefmt='%H:%M:%S'
            )
            handler.setFormatter(formatter)
            self.std_logger.addHandler(handler)
    
    def log_action(
        self,
        component: str,
        action: str,
        status: str,
        details: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None
    ):
        """
        Log an action to audit log.
        
        Args:
            component: Component name (e.g., 'odoo_service', 'facebook_service')
            action: Action performed (e.g., 'create_invoice', 'post_facebook')
            status: 'success' or 'error'
            details: Additional details about the action
            error: Error message if status is 'error'
        """
        if self.dry_run:
            self.std_logger.info(f"[DRY RUN] {component}.{action} - {status}")
            return
        
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            'timestamp': timestamp,
            'component': component,
            'action': action,
            'status': status,
            'details': details or {}
        }
        
        if error:
            log_entry['error'] = error
        
        # Append to log file
        self._append_to_log(log_entry)
        
        # Also log to standard output
        if status == 'success':
            self.std_logger.info(f"{component}.{action} - SUCCESS")
        else:
            self.std_logger.error(f"{component}.{action} - ERROR: {error}")
    
    def _append_to_log(self, log_entry: Dict[str, Any]):
        """Append log entry to JSON log file."""
        try:
            # Read existing logs
            with open(self.log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Append new entry
            logs.append(log_entry)
            
            # Write back
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.std_logger.error(f"Failed to write to audit log: {e}")
    
    def log_odoo_invoice(self, invoice_id: str, partner: str, amount: float, status: str, error: str = None):
        """
        Log Odoo invoice creation.
        
        Args:
            invoice_id: Invoice ID or number
            partner: Customer name
            amount: Invoice amount
            status: 'success' or 'error'
            error: Error message if failed
        """
        self.log_action(
            component='odoo_service',
            action='create_invoice',
            status=status,
            details={
                'invoice_id': invoice_id,
                'partner': partner,
                'amount': amount
            },
            error=error
        )
    
    def log_odoo_payment(self, payment_id: str, invoice_id: str, amount: float, status: str, error: str = None):
        """
        Log Odoo payment recording.
        
        Args:
            payment_id: Payment ID
            invoice_id: Invoice ID that was paid
            amount: Payment amount
            status: 'success' or 'error'
            error: Error message if failed
        """
        self.log_action(
            component='odoo_service',
            action='record_payment',
            status=status,
            details={
                'payment_id': payment_id,
                'invoice_id': invoice_id,
                'amount': amount
            },
            error=error
        )
    
    def log_facebook_post(self, post_id: str, message: str, status: str, error: str = None):
        """
        Log Facebook post creation.
        
        Args:
            post_id: Facebook post ID
            message: Post content
            status: 'success' or 'error'
            error: Error message if failed
        """
        self.log_action(
            component='facebook_service',
            action='post_facebook',
            status=status,
            details={
                'post_id': post_id,
                'message_length': len(message),
                'message_preview': message[:100]
            },
            error=error
        )
    
    def log_facebook_message(self, recipient: str, status: str, error: str = None):
        """
        Log Facebook message sending.
        
        Args:
            recipient: Recipient ID
            status: 'success' or 'error'
            error: Error message if failed
        """
        self.log_action(
            component='facebook_service',
            action='send_facebook_message',
            status=status,
            details={
                'recipient': recipient
            },
            error=error
        )
    
    def log_email_sent(self, to: str, subject: str, message_id: str, status: str, error: str = None):
        """
        Log email sending.
        
        Args:
            to: Recipient email
            subject: Email subject
            message_id: Gmail message ID
            status: 'success' or 'error'
            error: Error message if failed
        """
        self.log_action(
            component='email_service',
            action='send_email',
            status=status,
            details={
                'to': to,
                'subject': subject,
                'message_id': message_id
            },
            error=error
        )
    
    def log_whatsapp_sent(self, contact: str, status: str, error: str = None):
        """
        Log WhatsApp message sending.
        
        Args:
            contact: Contact name/number
            status: 'success' or 'error'
            error: Error message if failed
        """
        self.log_action(
            component='whatsapp_service',
            action='send_whatsapp',
            status=status,
            details={
                'contact': contact
            },
            error=error
        )
    
    def log_linkedin_post(self, post_id: str, visibility: str, status: str, error: str = None):
        """
        Log LinkedIn post creation.
        
        Args:
            post_id: LinkedIn post ID
            visibility: Post visibility (PUBLIC, CONNECTIONS, etc.)
            status: 'success' or 'error'
            error: Error message if failed
        """
        self.log_action(
            component='linkedin_service',
            action='post_linkedin',
            status=status,
            details={
                'post_id': post_id,
                'visibility': visibility
            },
            error=error
        )
    
    def log_error_recovery(self, component: str, action: str, attempt: int, max_attempts: int, error: str):
        """
        Log error recovery attempt.
        
        Args:
            component: Component name
            action: Action being retried
            attempt: Current attempt number
            max_attempts: Maximum retry attempts
            error: Error message
        """
        self.log_action(
            component='error_recovery',
            action='retry_attempt',
            status='retry',
            details={
                'component': component,
                'action': action,
                'attempt': attempt,
                'max_attempts': max_attempts
            },
            error=error
        )
    
    def log_orchestrator_action(self, action_type: str, category: str, item_name: str, status: str, error: str = None):
        """
        Log orchestrator actions.
        
        Args:
            action_type: Type of action (process, approve, reject)
            category: Category (email, whatsapp, odoo, facebook, etc.)
            item_name: Item being processed
            status: 'success' or 'error'
            error: Error message if failed
        """
        self.log_action(
            component='orchestrator',
            action=action_type,
            status=status,
            details={
                'category': category,
                'item_name': item_name
            },
            error=error
        )
    
    def get_today_logs(self) -> list:
        """
        Get all log entries for today.
        
        Returns:
            List of log entries
        """
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.std_logger.error(f"Failed to read audit log: {e}")
            return []
    
    def get_logs_by_component(self, component: str) -> list:
        """
        Get all log entries for a specific component.
        
        Args:
            component: Component name to filter by
            
        Returns:
            List of log entries for the component
        """
        logs = self.get_today_logs()
        return [log for log in logs if log.get('component') == component]
    
    def get_error_logs(self) -> list:
        """
        Get all error log entries.
        
        Returns:
            List of error log entries
        """
        logs = self.get_today_logs()
        return [log for log in logs if log.get('status') == 'error']
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary of today's audit logs.
        
        Returns:
            Summary statistics
        """
        logs = self.get_today_logs()
        
        summary = {
            'total_actions': len(logs),
            'success_count': 0,
            'error_count': 0,
            'by_component': {}
        }
        
        for log in logs:
            status = log.get('status', 'unknown')
            component = log.get('component', 'unknown')
            
            if status == 'success':
                summary['success_count'] += 1
            elif status == 'error':
                summary['error_count'] += 1
            
            if component not in summary['by_component']:
                summary['by_component'][component] = {'total': 0, 'success': 0, 'error': 0}
            
            summary['by_component'][component]['total'] += 1
            if status == 'success':
                summary['by_component'][component]['success'] += 1
            elif status == 'error':
                summary['by_component'][component]['error'] += 1
        
        return summary


# Global audit logger instance
_audit_logger = None


def get_audit_logger(vault_path: str = './AI_Employee_Vault_FTE') -> AuditLogger:
    """
    Get or create global audit logger instance.
    
    Args:
        vault_path: Path to Obsidian vault
        
    Returns:
        AuditLogger instance
    """
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger(vault_path)
    return _audit_logger

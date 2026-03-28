"""
Audit Logging & Error Recovery Package - Gold Tier

Comprehensive audit logging, retry logic, circuit breaker, and health checks.
"""

from .logger import AuditLogger, get_audit_logger
from .retry import retry, retry_sync
from .circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    get_circuit_breaker
)
from .health import (
    check_odoo_health,
    check_facebook_health,
    check_email_health,
    check_linkedin_health,
    check_whatsapp_health,
    get_all_health_statuses,
    clear_health_cache
)

__all__ = [
    # Logger
    'AuditLogger',
    'get_audit_logger',
    
    # Retry
    'retry',
    'retry_sync',
    
    # Circuit Breaker
    'CircuitBreaker',
    'CircuitBreakerOpenError',
    'get_circuit_breaker',
    
    # Health Checks
    'check_odoo_health',
    'check_facebook_health',
    'check_email_health',
    'check_linkedin_health',
    'check_whatsapp_health',
    'get_all_health_statuses',
    'clear_health_cache',
]

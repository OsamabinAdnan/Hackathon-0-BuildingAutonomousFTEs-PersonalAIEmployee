"""
Service Health Checker - Gold Tier

Check if services are healthy before making requests.

Usage:
    from audit.health import check_odoo_health, check_facebook_health
    
    if check_odoo_health():
        # Odoo is healthy, safe to use
        result = await odoo_service.create_invoice(...)
    else:
        # Odoo is down, use fallback or notify user
"""

import logging
import asyncio
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger('audit.health')


# Health status cache
_health_cache: Dict[str, dict] = {}
_cache_ttl = 60  # Cache health status for 60 seconds


def _get_cached_health(service: str) -> dict:
    """Get cached health status if still valid."""
    if service in _health_cache:
        cached = _health_cache[service]
        age = (datetime.now() - cached['timestamp']).total_seconds()
        if age < _cache_ttl:
            return cached
    return None


def _set_cached_health(service: str, healthy: bool, details: str = ""):
    """Cache health status."""
    _health_cache[service] = {
        'healthy': healthy,
        'details': details,
        'timestamp': datetime.now()
    }


async def check_odoo_health(
    url: str = "http://localhost:8069",
    db: str = "odoo_db",
    username: str = "admin",
    password: str = "admin"
) -> bool:
    """
    Check if Odoo service is healthy.
    
    Args:
        url: Odoo URL
        db: Database name
        username: Odoo username
        password: Odoo password
    
    Returns:
        True if healthy, False otherwise
    """
    # Check cache first
    cached = _get_cached_health('odoo')
    if cached:
        return cached['healthy']
    
    try:
        # Try to connect to Odoo
        from mcp_server.odoo_service import OdooService
        
        service = OdooService(
            url=url,
            db=db,
            username=username,
            password=password
        )
        
        if service._connect():
            _set_cached_health('odoo', True, 'Connected successfully')
            logger.info("Odoo health check: HEALTHY")
            return True
        else:
            _set_cached_health('odoo', False, 'Connection failed')
            logger.warning("Odoo health check: UNHEALTHY - Connection failed")
            return False
            
    except Exception as e:
        _set_cached_health('odoo', False, str(e))
        logger.warning(f"Odoo health check: UNHEALTHY - {str(e)}")
        return False


async def check_facebook_health(
    page_id: str = None,
    access_token: str = None
) -> bool:
    """
    Check if Facebook service is healthy.
    
    Args:
        page_id: Facebook Page ID
        access_token: Facebook Access Token
    
    Returns:
        True if healthy, False otherwise
    """
    # Check cache first
    cached = _get_cached_health('facebook')
    if cached:
        return cached['healthy']
    
    try:
        # Try to get page info
        from mcp_server.facebook_service import FacebookService
        
        service = FacebookService()
        result = await service.get_page_info()
        
        if result.get('success'):
            _set_cached_health('facebook', True, 'Page info retrieved')
            logger.info("Facebook health check: HEALTHY")
            return True
        else:
            _set_cached_health('facebook', False, result.get('error', 'Unknown error'))
            logger.warning(f"Facebook health check: UNHEALTHY - {result.get('error')}")
            return False
            
    except Exception as e:
        _set_cached_health('facebook', False, str(e))
        logger.warning(f"Facebook health check: UNHEALTHY - {str(e)}")
        return False


async def check_email_health() -> bool:
    """
    Check if Email service (Gmail) is healthy.
    
    Returns:
        True if healthy, False otherwise
    """
    # Check cache first
    cached = _get_cached_health('email')
    if cached:
        return cached['healthy']
    
    try:
        # Try to authenticate
        from mcp_server.email_service import EmailService
        
        service = EmailService()
        
        if service._authenticate():
            _set_cached_health('email', True, 'Authenticated successfully')
            logger.info("Email health check: HEALTHY")
            return True
        else:
            _set_cached_health('email', False, 'Authentication failed')
            logger.warning("Email health check: UNHEALTHY - Authentication failed")
            return False
            
    except Exception as e:
        _set_cached_health('email', False, str(e))
        logger.warning(f"Email health check: UNHEALTHY - {str(e)}")
        return False


async def check_linkedin_health() -> bool:
    """
    Check if LinkedIn service is healthy.
    
    Returns:
        True if healthy, False otherwise
    """
    # Check cache first
    cached = _get_cached_health('linkedin')
    if cached:
        return cached['healthy']
    
    try:
        # Try to get profile
        from mcp_server.linkedin_service import LinkedInService
        
        service = LinkedInService()
        result = await service.get_profile()
        
        if result.get('success'):
            _set_cached_health('linkedin', True, 'Profile retrieved')
            logger.info("LinkedIn health check: HEALTHY")
            return True
        else:
            _set_cached_health('linkedin', False, result.get('error', 'Unknown error'))
            logger.warning(f"LinkedIn health check: UNHEALTHY - {result.get('error')}")
            return False
            
    except Exception as e:
        _set_cached_health('linkedin', False, str(e))
        logger.warning(f"LinkedIn health check: UNHEALTHY - {str(e)}")
        return False


async def check_whatsapp_health() -> bool:
    """
    Check if WhatsApp service is healthy.
    
    Returns:
        True if healthy, False otherwise
    """
    # Check cache first
    cached = _get_cached_health('whatsapp')
    if cached:
        return cached['healthy']
    
    try:
        # WhatsApp health check is complex (requires browser)
        # For now, just check if session exists
        import os
        from pathlib import Path
        
        session_path = os.getenv('WHATSAPP_SESSION_PATH', './sessions/whatsapp')
        if Path(session_path).exists():
            _set_cached_health('whatsapp', True, 'Session exists')
            logger.info("WhatsApp health check: HEALTHY")
            return True
        else:
            _set_cached_health('whatsapp', False, 'Session not found')
            logger.warning("WhatsApp health check: UNHEALTHY - Session not found")
            return False
            
    except Exception as e:
        _set_cached_health('whatsapp', False, str(e))
        logger.warning(f"WhatsApp health check: UNHEALTHY - {str(e)}")
        return False


def get_all_health_statuses() -> Dict[str, bool]:
    """
    Get health status for all services.
    
    Returns:
        Dict with service names as keys and health status as values
    """
    return {
        service: data['healthy']
        for service, data in _health_cache.items()
    }


def clear_health_cache():
    """Clear all cached health statuses."""
    _health_cache.clear()
    logger.info("Health cache cleared")

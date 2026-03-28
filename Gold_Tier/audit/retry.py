"""
Retry Decorator - Gold Tier

Automatic retry with exponential backoff for failed operations.

Usage:
    @retry(max_attempts=3, delay=1, backoff=2)
    async def create_invoice(...):
        # Automatically retries on failure
"""

import asyncio
import logging
from functools import wraps
from typing import Optional, Callable, Any

from audit.logger import get_audit_logger

logger = logging.getLogger('audit.retry')


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1)
        backoff: Multiplier for delay after each retry (default: 2)
        exceptions: Tuple of exceptions to catch and retry (default: all)
    
    Returns:
        Decorated function with retry logic
    
    Example:
        @retry(max_attempts=3, delay=1, backoff=2)
        async def create_invoice(...):
            # Will retry up to 3 times with delays: 1s, 2s, 4s
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            audit_logger = get_audit_logger()
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    # Log retry attempt if not first try
                    if attempt > 1:
                        logger.warning(
                            f"Retry attempt {attempt}/{max_attempts} for {func.__name__}"
                        )
                        audit_logger.log_error_recovery(
                            component=func.__module__.split('.')[-1],
                            action=func.__name__,
                            attempt=attempt,
                            max_attempts=max_attempts,
                            error=str(last_exception) if last_exception else 'Unknown'
                        )
                    
                    # Execute the function
                    result = await func(*args, **kwargs)
                    
                    # Log success if this was a retry
                    if attempt > 1:
                        logger.info(
                            f"Retry succeeded for {func.__name__} on attempt {attempt}"
                        )
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    logger.error(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}"
                    )
                    
                    # If this was the last attempt, raise the exception
                    if attempt == max_attempts:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}"
                        )
                        raise
                    
                    # Wait before next attempt (exponential backoff)
                    wait_time = delay * (backoff ** (attempt - 1))
                    logger.info(f"Waiting {wait_time}s before next retry...")
                    await asyncio.sleep(wait_time)
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator


def retry_sync(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,)
):
    """
    Retry decorator for synchronous functions with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts (default: 3)
        delay: Initial delay between retries in seconds (default: 1)
        backoff: Multiplier for delay after each retry (default: 2)
        exceptions: Tuple of exceptions to catch and retry (default: all)
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            import time
            audit_logger = get_audit_logger()
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    # Log retry attempt if not first try
                    if attempt > 1:
                        logger.warning(
                            f"Retry attempt {attempt}/{max_attempts} for {func.__name__}"
                        )
                        audit_logger.log_error_recovery(
                            component=func.__module__.split('.')[-1],
                            action=func.__name__,
                            attempt=attempt,
                            max_attempts=max_attempts,
                            error=str(last_exception) if last_exception else 'Unknown'
                        )
                    
                    # Execute the function
                    result = func(*args, **kwargs)
                    
                    # Log success if this was a retry
                    if attempt > 1:
                        logger.info(
                            f"Retry succeeded for {func.__name__} on attempt {attempt}"
                        )
                    
                    return result
                    
                except exceptions as e:
                    last_exception = e
                    logger.error(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {str(e)}"
                    )
                    
                    # If this was the last attempt, raise the exception
                    if attempt == max_attempts:
                        logger.error(
                            f"All {max_attempts} attempts failed for {func.__name__}"
                        )
                        raise
                    
                    # Wait before next attempt (exponential backoff)
                    wait_time = delay * (backoff ** (attempt - 1))
                    logger.info(f"Waiting {wait_time}s before next retry...")
                    time.sleep(wait_time)
            
            # Should never reach here, but just in case
            raise last_exception
        
        return wrapper
    return decorator

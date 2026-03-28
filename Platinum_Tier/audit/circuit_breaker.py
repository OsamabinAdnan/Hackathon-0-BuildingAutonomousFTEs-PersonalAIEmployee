"""
Circuit Breaker - Gold Tier

Prevents repeated calls to failing services.

Usage:
    circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=300)
    
    @circuit_breaker
    async def create_invoice(...):
        # Will stop calling if service fails 3 times in a row
        # Will try again after 5 minutes
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Optional, Callable, Any, Dict
from enum import Enum

from audit.logger import get_audit_logger

logger = logging.getLogger('audit.circuit_breaker')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation, requests allowed
    OPEN = "open"         # Service failing, requests blocked
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents repeated calls to failing services by:
    1. Tracking consecutive failures
    2. Opening circuit after threshold failures
    3. Blocking requests for recovery timeout
    4. Testing with half-open state
    5. Closing circuit on success
    
    Attributes:
        failure_threshold: Number of failures before opening circuit (default: 3)
        recovery_timeout: Seconds to wait before testing again (default: 300 = 5 min)
        half_open_max_calls: Max calls in half-open state (default: 1)
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout: int = 300,
        half_open_max_calls: int = 1
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before testing recovery
            half_open_max_calls: Test calls allowed in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        # State tracking
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.half_open_calls = 0
        
        # Per-function tracking
        self._function_states: Dict[str, dict] = {}
    
    def _get_function_state(self, func_name: str) -> dict:
        """Get or create state for a specific function."""
        if func_name not in self._function_states:
            self._function_states[func_name] = {
                'state': CircuitState.CLOSED,
                'failure_count': 0,
                'success_count': 0,
                'last_failure_time': None,
                'half_open_calls': 0
            }
        return self._function_states[func_name]
    
    def __call__(self, func: Callable) -> Callable:
        """
        Decorator to add circuit breaker to function.
        
        Args:
            func: Function to wrap
        
        Returns:
            Wrapped function with circuit breaker logic
        """
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            audit_logger = get_audit_logger()
            func_name = func.__name__
            func_state = self._get_function_state(func_name)
            
            # Check if circuit is open
            if func_state['state'] == CircuitState.OPEN:
                # Check if recovery timeout has passed
                if func_state['last_failure_time']:
                    time_since_failure = time.time() - func_state['last_failure_time']
                    if time_since_failure >= self.recovery_timeout:
                        # Transition to half-open
                        func_state['state'] = CircuitState.HALF_OPEN
                        func_state['half_open_calls'] = 0
                        logger.info(
                            f"Circuit breaker for {func_name} transitioning to HALF-OPEN"
                        )
                    else:
                        # Still in recovery timeout, block request
                        remaining = int(self.recovery_timeout - time_since_failure)
                        logger.warning(
                            f"Circuit breaker OPEN for {func_name}. "
                            f"Retry in {remaining}s"
                        )
                        audit_logger.log_action(
                            component='circuit_breaker',
                            action='block_request',
                            status='blocked',
                            details={
                                'function': func_name,
                                'reason': 'circuit_open',
                                'retry_in': remaining
                            }
                        )
                        raise CircuitBreakerOpenError(
                            f"Circuit breaker open for {func_name}. Retry in {remaining}s"
                        )
            
            # Check if in half-open state and exceeded max calls
            if func_state['state'] == CircuitState.HALF_OPEN:
                if func_state['half_open_calls'] >= self.half_open_max_calls:
                    logger.warning(
                        f"Circuit breaker HALF-OPEN limit reached for {func_name}"
                    )
                    raise CircuitBreakerOpenError(
                        f"Half-open call limit reached for {func_name}"
                    )
                func_state['half_open_calls'] += 1
            
            try:
                # Execute function
                result = await func(*args, **kwargs)
                
                # Success - update state
                self._on_success(func_name)
                
                return result
                
            except Exception as e:
                # Failure - update state
                self._on_failure(func_name, str(e))
                raise
        
        return wrapper
    
    def _on_success(self, func_name: str):
        """Handle successful call."""
        func_state = self._get_function_state(func_name)
        func_state['success_count'] += 1
        
        if func_state['state'] == CircuitState.HALF_OPEN:
            # Success in half-open state, close circuit
            func_state['state'] = CircuitState.CLOSED
            func_state['failure_count'] = 0
            logger.info(f"Circuit breaker for {func_name} CLOSED (recovered)")
        elif func_state['state'] == CircuitState.CLOSED:
            # Reset failure count on success
            func_state['failure_count'] = 0
    
    def _on_failure(self, func_name: str, error: str):
        """Handle failed call."""
        func_state = self._get_function_state(func_name)
        func_state['failure_count'] += 1
        func_state['last_failure_time'] = time.time()
        
        logger.error(f"Circuit breaker failure for {func_name}: {error}")
        
        if func_state['state'] == CircuitState.HALF_OPEN:
            # Failure in half-open state, open circuit again
            func_state['state'] = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker for {func_name} re-OPENED (recovery failed)"
            )
        elif func_state['state'] == CircuitState.CLOSED:
            # Check if threshold reached
            if func_state['failure_count'] >= self.failure_threshold:
                func_state['state'] = CircuitState.OPEN
                logger.warning(
                    f"Circuit breaker for {func_name} OPENED "
                    f"({func_state['failure_count']} failures)"
                )
    
    def get_state(self, func_name: str) -> str:
        """
        Get current state for a function.
        
        Args:
            func_name: Function name
        
        Returns:
            Current circuit state ('closed', 'open', 'half_open')
        """
        func_state = self._get_function_state(func_name)
        return func_state['state'].value
    
    def reset(self, func_name: str):
        """
        Reset circuit breaker for a function.
        
        Args:
            func_name: Function name
        """
        self._function_states[func_name] = {
            'state': CircuitState.CLOSED,
            'failure_count': 0,
            'success_count': 0,
            'last_failure_time': None,
            'half_open_calls': 0
        }
        logger.info(f"Circuit breaker for {func_name} reset")


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open and blocking requests."""
    pass


# Global circuit breaker instance
_circuit_breaker = None


def get_circuit_breaker() -> CircuitBreaker:
    """
    Get or create global circuit breaker instance.
    
    Returns:
        CircuitBreaker instance
    """
    global _circuit_breaker
    if _circuit_breaker is None:
        _circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=300,  # 5 minutes
            half_open_max_calls=1
        )
    return _circuit_breaker

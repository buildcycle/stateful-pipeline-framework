"""Retry mechanism for step execution."""

import time
from typing import Callable, Optional, Tuple, Any
from .errors import RetryExhaustedError


class RetryConfig:
    """Configuration for retry behavior."""
    
    def __init__(
        self,
        max_attempts: int = 3,
        delay: float = 1.0,
        backoff_multiplier: float = 2.0,
        retry_on: Optional[Callable[[Exception], bool]] = None
    ):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_multiplier = backoff_multiplier
        self.retry_on = retry_on or (lambda e: True)
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """Determine if we should retry based on error and attempt count."""
        if attempt >= self.max_attempts:
            return False
        return self.retry_on(error)


def retry_step(
    step_name: str,
    execute_fn: Callable,
    retry_config: RetryConfig,
    attempt: int = 0
) -> Tuple[Any, int]:
    """
    Execute a step with retry logic.
    
    Args:
        step_name: Name of the step being executed
        execute_fn: Function to execute (should be step.execute)
        retry_config: Retry configuration
        attempt: Current attempt number (0-indexed)
        
    Returns:
        Tuple of (result, total_attempts)
        
    Raises:
        RetryExhaustedError: If all retry attempts are exhausted
    """
    try:
        result = execute_fn()
        return result, attempt + 1
    except Exception as e:
        if retry_config.should_retry(e, attempt):
            delay = retry_config.delay * (retry_config.backoff_multiplier ** attempt)
            time.sleep(delay)
            return retry_step(step_name, execute_fn, retry_config, attempt + 1)
        else:
            raise RetryExhaustedError(step_name, attempt + 1) from e


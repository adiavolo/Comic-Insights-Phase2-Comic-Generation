"""Status tracking utilities for UI components.

This module provides decorators and utilities for tracking the status of operations
in UI components, including the track_status decorator which adds status logging
to function calls.
"""

import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)

def track_status(component_name: str) -> Callable:
    """Decorator to track the status of operations in UI components.
    
    This decorator adds logging before and after the decorated function is called,
    providing status information about the operation.
    
    Args:
        component_name (str): The name of the component being tracked
        
    Returns:
        Callable: The decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            logger.info(f"Starting {component_name} operation: {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Completed {component_name} operation: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"Failed {component_name} operation: {func.__name__} - {str(e)}")
                raise
        return wrapper
    return decorator 
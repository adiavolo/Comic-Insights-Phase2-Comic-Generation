"""Logging utilities for UI components.

This module provides logging functionality specifically designed for UI components,
including the ComponentLogger class which adds component-specific context to log messages.
"""

import logging
from typing import Optional

class ComponentLogger:
    """Logger class for UI components with component-specific context.
    
    This logger adds component-specific information to log messages and provides
    convenient methods for logging at different levels.
    
    Attributes:
        name (str): The name of the component using this logger
        logger (logging.Logger): The underlying Python logger instance
    """
    
    def __init__(self, name: str):
        """Initialize the component logger.
        
        Args:
            name (str): The name of the component (usually __name__)
        """
        self.name = name
        self.logger = logging.getLogger(name)
    
    def debug(self, msg: str, *args, **kwargs):
        """Log a debug message.
        
        Args:
            msg (str): The message to log
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.debug(f"[{self.name}] {msg}", *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log an info message.
        
        Args:
            msg (str): The message to log
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.info(f"[{self.name}] {msg}", *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log a warning message.
        
        Args:
            msg (str): The message to log
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.warning(f"[{self.name}] {msg}", *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log an error message.
        
        Args:
            msg (str): The message to log
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.error(f"[{self.name}] {msg}", *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log a critical message.
        
        Args:
            msg (str): The message to log
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.critical(f"[{self.name}] {msg}", *args, **kwargs)
    
    def exception(self, msg: str, *args, **kwargs):
        """Log an exception message.
        
        Args:
            msg (str): The message to log
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        self.logger.exception(f"[{self.name}] {msg}", *args, **kwargs) 
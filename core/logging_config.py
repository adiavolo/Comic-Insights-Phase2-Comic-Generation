import logging
import logging.handlers
import os
from datetime import datetime
from pathlib import Path
import json
from typing import Dict, Any
import sys
from pythonjsonlogger import jsonlogger

class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        if not log_record.get('timestamp'):
            log_record['timestamp'] = datetime.utcnow().isoformat()
        if log_record.get('level'):
            log_record['level'] = log_record['level'].upper()
        else:
            log_record['level'] = record.levelname

class ColoredConsoleFormatter(logging.Formatter):
    """Custom formatter for colored console output"""
    
    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    green = "\x1b[32;20m"
    
    FORMATS = {
        logging.DEBUG: grey + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.INFO: green + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.WARNING: yellow + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.ERROR: red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset,
        logging.CRITICAL: bold_red + "%(asctime)s - %(name)s - %(levelname)s - %(message)s" + reset
    }
    
    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

class LogConfig:
    def __init__(self, log_dir: str = "logs", console_output: bool = True):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.console_output = console_output
        
        # Create subdirectories for different log types
        (self.log_dir / "debug").mkdir(exist_ok=True)
        (self.log_dir / "error").mkdir(exist_ok=True)
        (self.log_dir / "status").mkdir(exist_ok=True)
        
        self.setup_logging()
    
    def setup_logging(self):
        # Main logger configuration
        logging.basicConfig(level=logging.INFO)
        
        # Create loggers
        self.setup_debug_logger()
        self.setup_error_logger()
        self.setup_status_logger()
        
        if self.console_output:
            self.setup_console_handler()
    
    def setup_console_handler(self):
        """Set up colored console output"""
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(ColoredConsoleFormatter())
        
        # Add console handler to all loggers
        for logger_name in ['comic_insights.debug', 'comic_insights.error', 'comic_insights.status']:
            logger = logging.getLogger(logger_name)
            logger.addHandler(console_handler)
    
    def setup_debug_logger(self):
        debug_logger = logging.getLogger('comic_insights.debug')
        debug_logger.setLevel(logging.DEBUG)
        debug_logger.propagate = False
        
        # File handler for debug logs
        debug_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "debug" / "debug.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        debug_handler.setFormatter(CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(funcName)s:%(lineno)d %(message)s'
        ))
        debug_logger.addHandler(debug_handler)
    
    def setup_error_logger(self):
        error_logger = logging.getLogger('comic_insights.error')
        error_logger.setLevel(logging.ERROR)
        error_logger.propagate = False
        
        # File handler for error logs
        error_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "error" / "error.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        error_handler.setFormatter(CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(funcName)s:%(lineno)d %(message)s %(exc_info)s'
        ))
        error_logger.addHandler(error_handler)
    
    def setup_status_logger(self):
        status_logger = logging.getLogger('comic_insights.status')
        status_logger.setLevel(logging.INFO)
        status_logger.propagate = False
        
        # File handler for status logs
        status_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / "status" / "status.log",
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        status_handler.setFormatter(CustomJsonFormatter(
            '%(timestamp)s %(level)s %(message)s %(status_data)s'
        ))
        status_logger.addHandler(status_handler)

def get_logger(name: str) -> logging.Logger:
    """Get a logger by name with proper configuration"""
    return logging.getLogger(f'comic_insights.{name}')

# Status tracking decorator with enhanced metrics
def track_status(component: str):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger = get_logger('status')
            start_time = datetime.now()
            
            # Get initial resource usage
            try:
                import psutil
                process = psutil.Process()
                initial_memory = process.memory_info().rss
                initial_cpu = process.cpu_percent()
            except ImportError:
                initial_memory = initial_cpu = None
            
            status_data = {
                'component': component,
                'function': func.__name__,
                'start_time': start_time.isoformat(),
                'status': 'started',
                'args': str(args),
                'kwargs': str(kwargs),
                'initial_metrics': {
                    'memory_usage': initial_memory,
                    'cpu_percent': initial_cpu
                }
            }
            
            # Log start
            logger.info(f"{component} operation started", extra={'status_data': status_data})
            
            try:
                result = func(*args, **kwargs)
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Get final resource usage
                try:
                    final_memory = process.memory_info().rss
                    final_cpu = process.cpu_percent()
                    memory_diff = final_memory - initial_memory if initial_memory else None
                except:
                    final_memory = final_cpu = memory_diff = None
                
                status_data.update({
                    'status': 'completed',
                    'duration': duration,
                    'end_time': end_time.isoformat(),
                    'final_metrics': {
                        'memory_usage': final_memory,
                        'memory_diff': memory_diff,
                        'cpu_percent': final_cpu
                    }
                })
                
                # Log completion
                logger.info(f"{component} operation completed", extra={'status_data': status_data})
                return result
                
            except Exception as e:
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                # Get error state resource usage
                try:
                    error_memory = process.memory_info().rss
                    error_cpu = process.cpu_percent()
                    memory_diff = error_memory - initial_memory if initial_memory else None
                except:
                    error_memory = error_cpu = memory_diff = None
                
                status_data.update({
                    'status': 'failed',
                    'error': str(e),
                    'duration': duration,
                    'end_time': end_time.isoformat(),
                    'error_metrics': {
                        'memory_usage': error_memory,
                        'memory_diff': memory_diff,
                        'cpu_percent': error_cpu
                    }
                })
                
                # Log error
                error_logger = get_logger('error')
                error_logger.exception(f"{component} operation failed", extra={'status_data': status_data})
                raise
                
        return wrapper
    return decorator 
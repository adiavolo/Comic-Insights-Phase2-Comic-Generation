from ui.interface import create_interface
import logging
import os
from core.logging_config import LogConfig
from datetime import datetime
import gradio as gr
import sys
import psutil
import platform
from backend import nlp_engine, session_manager

def get_system_info() -> dict:
    """Get detailed system information for logging"""
    return {
        'python_version': sys.version,
        'platform': platform.platform(),
        'processor': platform.processor(),
        'memory': {
            'total': psutil.virtual_memory().total,
            'available': psutil.virtual_memory().available,
            'percent': psutil.virtual_memory().percent
        },
        'disk': {
            'total': psutil.disk_usage('/').total,
            'free': psutil.disk_usage('/').free,
            'percent': psutil.disk_usage('/').percent
        }
    }

def setup_environment():
    """Set up the application environment and logging"""
    # Initialize logging
    log_config = LogConfig()
    
    # Set up directories
    directories = ['logs', 'export', 'temp']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logging.getLogger('comic_insights.debug').debug(f"Created directory: {directory}")
    
    # Initialize backend components
    nlp_engine.initialize()
    # Session manager is already initialized in __init__.py

def main():
    start_time = None  # Initialize start_time at the beginning
    try:
        # Set up environment and logging
        setup_environment()
        logger = logging.getLogger('comic_insights.debug')
        status_logger = logging.getLogger('comic_insights.status')
        error_logger = logging.getLogger('comic_insights.error')
        
        start_time = datetime.now()  # Set start_time after successful setup
        logger.info("Starting Comic Insights application")
        
        # Get system information
        sys_info = get_system_info()
        
        # Log application start with detailed system info
        status_logger.info(
            "Application startup",
            extra={
                'status_data': {
                    'start_time': start_time.isoformat(),
                    'system_info': sys_info,
                    'working_directory': os.getcwd(),
                    'gradio_version': gr.__version__
                }
            }
        )
        
        try:
            # Create and launch the interface
            demo = create_interface()
            
            # Log successful interface creation
            status_logger.info(
                "Interface created successfully",
                extra={
                    'status_data': {
                        'gradio_version': gr.__version__,
                        'interface_type': 'blocks',
                        'memory_usage': psutil.Process().memory_info().rss
                    }
                }
            )
            
            # Launch the interface with error handling
            try:
                demo.launch(
                    server_name="0.0.0.0",
                    server_port=7861,
                    share=False
                )
                
                # Log successful launch
                status_logger.info(
                    "Interface launched successfully",
                    extra={
                        'status_data': {
                            'server': "0.0.0.0",
                            'port': 7861,
                            'share': False,
                            'memory_usage': psutil.Process().memory_info().rss
                        }
                    }
                )
            except Exception as launch_error:
                error_logger.exception(
                    "Failed to launch interface",
                    extra={
                        'error': str(launch_error),
                        'traceback': True,
                        'server_config': {
                            'server': "0.0.0.0",
                            'port': 7861,
                            'share': False
                        }
                    }
                )
                raise
            
        except Exception as interface_error:
            error_logger.exception(
                "Failed to create interface",
                extra={
                    'error': str(interface_error),
                    'traceback': True,
                    'memory_usage': psutil.Process().memory_info().rss
                }
            )
            raise
            
    except Exception as e:
        error_logger = logging.getLogger('comic_insights.error')
        error_logger.exception(
            "Critical application error",
            extra={
                'error': str(e),
                'traceback': True,
                'memory_usage': psutil.Process().memory_info().rss if 'psutil' in sys.modules else 'N/A'
            }
        )
        raise
    finally:
        # Log application shutdown if we get here
        if start_time:  # Only calculate duration if start_time was set
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            try:
                memory_usage = psutil.Process().memory_info().rss
            except:
                memory_usage = 'N/A'
            
            status_logger = logging.getLogger('comic_insights.status')
            status_logger.info(
                "Application shutdown",
                extra={
                    'status_data': {
                        'end_time': end_time.isoformat(),
                        'duration': duration,
                        'shutdown_type': 'clean' if 'e' not in locals() else 'error',
                        'memory_usage': memory_usage,
                        'system_status': {
                            'cpu_percent': psutil.cpu_percent(),
                            'memory_percent': psutil.virtual_memory().percent,
                            'disk_usage': psutil.disk_usage('/').percent
                        }
                    }
                }
            )

if __name__ == "__main__":
    main() 
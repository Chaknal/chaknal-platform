"""
Centralized Logging Configuration for Chaknal Platform
Provides structured logging across the application
"""

import logging
import sys
from datetime import datetime
from typing import Optional
import json

class ChaknalLogger:
    """Custom logger for Chaknal Platform with structured logging"""
    
    def __init__(self, name: str = "chaknal"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler if not already added
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """Log info message with optional context"""
        context = {"context": kwargs} if kwargs else {}
        self.logger.info(f"{message} | {json.dumps(context)}" if context else message)
    
    def error(self, message: str, **kwargs):
        """Log error message with optional context"""
        context = {"context": kwargs} if kwargs else {}
        self.logger.error(f"{message} | {json.dumps(context)}" if context else message)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with optional context"""
        context = {"context": kwargs} if kwargs else {}
        self.logger.warning(f"{message} | {json.dumps(context)}" if context else message)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with optional context"""
        context = {"context": kwargs} if kwargs else {}
        self.logger.debug(f"{message} | {json.dumps(context)}" if context else message)

# Global logger instance
logger = ChaknalLogger()

def get_logger(name: str = "chaknal") -> ChaknalLogger:
    """Get a logger instance"""
    return ChaknalLogger(name)

# Logging decorators
def log_function_call(func):
    """Decorator to log function calls"""
    def wrapper(*args, **kwargs):
        logger.info(f"🔧 Calling function: {func.__name__}", 
                   function=func.__name__, 
                   args=str(args), 
                   kwargs=str(kwargs))
        try:
            result = func(*args, **kwargs)
            logger.info(f"✅ Function {func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"❌ Function {func.__name__} failed", 
                         error=str(e), 
                         error_type=type(e).__name__)
            raise
    return wrapper

def log_api_call(endpoint: str, method: str = "GET"):
    """Decorator to log API calls"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info(f"🌐 API Call: {method} {endpoint}", 
                       endpoint=endpoint, 
                       method=method)
            try:
                result = func(*args, **kwargs)
                logger.info(f"✅ API Call successful: {method} {endpoint}")
                return result
            except Exception as e:
                logger.error(f"❌ API Call failed: {method} {endpoint}", 
                             error=str(e), 
                             error_type=type(e).__name__)
                raise
        return wrapper
    return decorator

"""
Logging Configuration for Chaknal Platform

This module provides comprehensive logging configuration including:
- Structured logging with JSON format
- Log rotation and retention
- Different log levels for different environments
- Integration with monitoring systems
"""

import logging
import logging.handlers
import sys
import os
from datetime import datetime
from typing import Dict, Any
import json
from pathlib import Path

# Create logs directory if it doesn't exist
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process_id": record.process,
            "thread_id": record.thread,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class StructuredLogger:
    """Enhanced logger with structured logging capabilities"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Set up logging handlers"""
        # Console handler with color formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with JSON formatting
        file_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "chaknal-platform.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        json_formatter = JSONFormatter()
        file_handler.setFormatter(json_formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.handlers.RotatingFileHandler(
            LOGS_DIR / "chaknal-platform-error.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(json_formatter)
        self.logger.addHandler(error_handler)
    
    def log_with_context(self, level: str, message: str, **kwargs):
        """Log message with additional context"""
        extra_fields = kwargs.copy()
        record = self.logger.makeRecord(
            self.logger.name, getattr(logging, level.upper()), 
            "", 0, message, (), None
        )
        record.extra_fields = extra_fields
        self.logger.handle(record)
    
    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.log_with_context("INFO", message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.log_with_context("WARNING", message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self.log_with_context("ERROR", message, **kwargs)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.log_with_context("DEBUG", message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with context"""
        self.log_with_context("CRITICAL", message, **kwargs)

def setup_logging(environment: str = "development") -> None:
    """Set up logging configuration for the application"""
    
    # Set root logger level
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Set specific logger levels
    loggers = {
        "app": logging.INFO,
        "app.services": logging.INFO,
        "app.api": logging.INFO,
        "app.models": logging.WARNING,
        "sqlalchemy": logging.WARNING,
        "uvicorn": logging.INFO,
        "fastapi": logging.INFO,
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)
    
    # Environment-specific logging
    if environment == "production":
        # Production: More verbose logging
        logging.getLogger("app.services.duxwrap_new").setLevel(logging.INFO)
        logging.getLogger("app.services.linkedin_automation").setLevel(logging.INFO)
    else:
        # Development: Debug logging
        logging.getLogger("app.services.duxwrap_new").setLevel(logging.DEBUG)
        logging.getLogger("app.services.linkedin_automation").setLevel(logging.DEBUG)

def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance"""
    return StructuredLogger(name)

# Specialized loggers for different components
def get_dux_wrapper_logger() -> StructuredLogger:
    """Get logger for DuxSoup wrapper operations"""
    return get_logger("app.services.duxwrap")

def get_automation_logger() -> StructuredLogger:
    """Get logger for LinkedIn automation operations"""
    return get_logger("app.services.automation")

def get_campaign_logger() -> StructuredLogger:
    """Get logger for campaign operations"""
    return get_logger("app.services.campaign")

def get_api_logger() -> StructuredLogger:
    """Get logger for API operations"""
    return get_logger("app.api")

# Logging middleware for FastAPI
class LoggingMiddleware:
    """Middleware to log all HTTP requests and responses"""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger("app.middleware")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = datetime.utcnow()
            
            # Log request
            self.logger.info(
                "HTTP Request",
                method=scope["method"],
                path=scope["path"],
                client_ip=scope.get("client", ["unknown"])[0],
                user_agent=dict(scope.get("headers", [])).get(b"user-agent", b"").decode(),
                timestamp=start_time.isoformat()
            )
            
            # Process request
            await self.app(scope, receive, send)
            
            # Log response time
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.info(
                "HTTP Response",
                method=scope["method"],
                path=scope["path"],
                duration_seconds=duration,
                timestamp=end_time.isoformat()
            )

# Performance monitoring
class PerformanceLogger:
    """Logger for performance metrics"""
    
    def __init__(self, operation: str):
        self.operation = operation
        self.start_time = datetime.utcnow()
        self.logger = get_logger("app.performance")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.utcnow() - self.start_time).total_seconds()
        
        if exc_type:
            self.logger.error(
                "Operation failed",
                operation=self.operation,
                duration_seconds=duration,
                error_type=exc_type.__name__,
                error_message=str(exc_val)
            )
        else:
            self.logger.info(
                "Operation completed",
                operation=self.operation,
                duration_seconds=duration
            )

# Usage examples:
# logger = get_logger("my_module")
# logger.info("User logged in", user_id="123", action="login")
# 
# with PerformanceLogger("database_query"):
#     # ... database operation
#     pass

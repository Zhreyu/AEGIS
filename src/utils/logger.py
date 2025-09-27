"""
Logging Utilities

This module contains logging configuration and utilities for the AEGIS system.
"""

import logging
import sys
from typing import Optional
from config.settings import config


def setup_logger(name: str = "aegis", level: Optional[str] = None) -> logging.Logger:
    """
    Set up a logger for the AEGIS system.
    
    Args:
        name (str): Logger name
        level (Optional[str]): Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(name)
    
    # Avoid adding multiple handlers
    if logger.handlers:
        return logger
    
    # Set log level
    log_level = level or config.LOG_LEVEL
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Create formatter
    formatter = logging.Formatter(config.LOG_FORMAT)
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(console_handler)
    
    return logger


def get_logger(name: str = "aegis") -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)

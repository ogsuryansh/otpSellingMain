"""
Logging Configuration Module
"""

import logging
import sys
from datetime import datetime
import os

def setup_logging():
    """Setup comprehensive logging configuration"""
    
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create file handler for all logs
    file_handler = logging.FileHandler(
        f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Create file handler for errors only
    error_handler = logging.FileHandler(
        f'logs/errors_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(error_handler)
    root_logger.addHandler(console_handler)
    
    # Setup specific loggers
    loggers = [
        'src.handlers.callback_handler',
        'src.handlers.start_handler',
        'src.handlers.admin_handler',
        'src.database.user_db',
        'src.config.bot_config',
        'src.utils.keyboard_utils'
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True
    
    # Log startup message
    logging.info("🚀 Bot logging system initialized")
    logging.info("📁 Log files will be saved in 'logs/' directory")
    logging.info("🔍 Debug logs: bot_YYYYMMDD.log")
    logging.info("❌ Error logs: errors_YYYYMMDD.log")

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)


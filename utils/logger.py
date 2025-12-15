"""Logging configuration for the system."""

import logging
import os
from typing import Dict


def setup_logging(config: Dict) -> logging.Logger:
    """
    Setup logging based on configuration.

    Args:
        config: Configuration dictionary

    Returns:
        Configured logger
    """
    log_config = config.get('logging', {})
    level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', 'results/logs/app.log')
    console = log_config.get('console', True)

    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logging
    handlers = []

    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        )
        handlers.append(file_handler)

    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(
            logging.Formatter('%(levelname)s - %(name)s - %(message)s')
        )
        handlers.append(console_handler)

    logging.basicConfig(
        level=level,
        handlers=handlers
    )

    return logging.getLogger('ExcelCleaner')

"""Helper utility functions."""

import json
import os
from datetime import datetime
from typing import Dict, Any


def get_timestamp() -> str:
    """
    Get current timestamp string.

    Returns:
        Timestamp in format YYYYMMDD_HHMMSS
    """
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_json(data: Dict, file_path: str) -> None:
    """
    Save dictionary as JSON file.

    Args:
        data: Dictionary to save
        file_path: Output file path
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def load_json(file_path: str) -> Dict:
    """
    Load JSON file as dictionary.

    Args:
        file_path: JSON file path

    Returns:
        Loaded dictionary
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def ensure_dir(directory: str) -> None:
    """
    Ensure directory exists, create if not.

    Args:
        directory: Directory path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def truncate_text(text: str, max_length: int = 1000) -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "... [truncated]"

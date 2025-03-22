import os
import shutil
import subprocess
from typing import Tuple


def get_terminal_size(
    default_width: int = 80, default_height: int = 24
) -> Tuple[int, int]:
    """
    Detect terminal size using multiple fallback methods.

    Args:
        default_width (int, optional): Default terminal width. Defaults to 80.
        default_height (int, optional): Default terminal height. Defaults to 24.

    Returns:
        Tuple[int, int]: A tuple of (width, height) representing terminal dimensions.
    """
    # Method 1: Use shutil.get_terminal_size (most reliable)
    try:
        terminal_size = shutil.get_terminal_size()
        return terminal_size.columns, terminal_size.lines
    except (OSError, AttributeError):
        pass

    # Method 2: Use stty (Unix-like systems)
    try:
        size_output = subprocess.check_output(["stty", "size"]).decode().strip().split()
        term_height, term_width = map(int, size_output)
        return term_width, term_height
    except (subprocess.SubprocessError, FileNotFoundError):
        pass

    # Method 3: Use environment variables (less reliable)
    try:
        width = os.environ.get("COLUMNS")
        height = os.environ.get("LINES")
        if width and height:
            return int(width), int(height)
    except (TypeError, ValueError):
        pass

    # Fallback to default values
    return default_width, default_height

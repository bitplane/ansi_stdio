#!/usr/bin/env python3
"""
Terminal output quantizer - captures terminal output at specified frame rate.

Usage:
    ./quantize.py [options] script.py

Examples:
    ./quantize.py --fps 2 my_script.py
    ./quantize.py --width 120 --height 40 --fps 5 my_script.py
"""

import argparse
import time
from typing import Optional

from ansi_stdio.terminal.capture import capture_terminal
from ansi_stdio.terminal.info import get_terminal_size
from ansi_stdio.terminal.render import display_dirty_lines


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Quantize terminal output from a Python script."
    )
    parser.add_argument("script", type=str, help="Python script to run and capture")
    parser.add_argument(
        "--width",
        type=int,
        default=None,
        help="Width of the terminal (default: detected)",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=None,
        help="Height of the terminal (default: detected)",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=1.0,
        help="Frames per second for output capture (default: 1.0)",
    )
    return parser.parse_args()


def quantize_output(
    script: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    fps: float = 1.0,
):
    """
    Capture and quantize terminal output from a Python script.

    Args:
        script (str): Path to the Python script to run
        width (int, optional): Terminal width
        height (int, optional): Terminal height
        fps (float, optional): Output frames per second
    """
    # Determine terminal dimensions
    if width is None or height is None:
        detected_width, detected_height = get_terminal_size()
        width = width or detected_width
        height = height or detected_height

    # Calculate time between frames
    frame_interval = 1.0 / fps
    last_dump_time = 0

    def quantized_display_callback(screen):
        nonlocal last_dump_time
        current_time = time.time()

        # Only dump if enough time has passed since last dump
        if current_time - last_dump_time >= frame_interval:
            display_dirty_lines(screen)
            last_dump_time = current_time

    # Capture terminal output with quantized display
    command = f"{script}"
    capture_terminal(
        program=command,
        width=width,
        height=height,
        display_callback=quantized_display_callback,
    )


def main():
    """Main entry point for the terminal quantizer."""
    args = parse_arguments()

    try:
        quantize_output(
            script=args.script, width=args.width, height=args.height, fps=args.fps
        )
    except Exception as e:
        print(f"Error running script: {e}")
        raise


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
A simple test for pyte terminal emulation.
Captures and displays program output using the capture_terminal function.

Usage:
    ./test.py [--program PROGRAM] [--width WIDTH] [--height HEIGHT]

Examples:
    ./test.py --program "ls -la" --width 100 --height 30
    ./test.py --program "cmatrix" --width 80 --height 25
"""

import argparse

from ansi_stdio.terminal.capture import capture_terminal
from ansi_stdio.terminal.info import get_terminal_size
from ansi_stdio.terminal.render import display_dirty_lines, display_screen


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Process and display terminal output with customizable size."
    )
    parser.add_argument(
        "--program",
        type=str,
        help="Program to run and capture (e.g. 'ls -la')",
        required=True,
    )
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
        "--delta",
        action="store_true",
        help="Use delta updates instead of full screen updates",
    )
    return parser.parse_args()


def main():
    """
    Main function to run a program and display its output using pyte.
    """
    args = parse_arguments()

    # Use get_terminal_size to detect terminal dimensions if not specified
    terminal_width = args.width
    terminal_height = args.height

    if terminal_width is None or terminal_height is None:
        # Detect terminal size and use detected values for unspecified dimensions
        detected_width, detected_height = get_terminal_size()
        terminal_width = args.width or detected_width
        terminal_height = args.height or detected_height

    # Clear the screen
    print("\033[H\033[J", end="", flush=True)
    print(f"Terminal size: {terminal_width}x{terminal_height}")
    print(f"Running program: {args.program}")
    print(f"Using {'delta' if args.delta else 'full'} screen updates")

    # Capture terminal output
    capture_display_callback = display_dirty_lines if args.delta else display_screen

    try:
        capture_terminal(
            program=args.program,
            width=terminal_width,
            height=terminal_height,
            display_callback=capture_display_callback,
        )
        print("Done!")
    except Exception as e:
        print(f"\nError running program: {e}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
A simple test for pyte terminal emulation.
Captures and displays program output using the pyte_renderer module.

Usage:
    ./test.py [--program PROGRAM] [--width WIDTH] [--height HEIGHT]

Examples:
    ./test.py --program "ls -la" --width 100 --height 30
    ./test.py --program "cmatrix" --width 80 --height 25
"""

import argparse
import errno
import os
import subprocess
import time

import pyte

from ansi_stdio.buffer.pyte_renderer import display_dirty_lines, display_screen


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
        "--width", type=int, default=80, help="Width of the terminal (default: 80)"
    )
    parser.add_argument(
        "--height", type=int, default=24, help="Height of the terminal (default: 24)"
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

    terminal_width = args.width
    terminal_height = args.height

    # Override with terminal size if available and no custom size was specified
    if not args.width or not args.height:
        try:
            # Try to get size using stty
            size_output = (
                subprocess.check_output(["stty", "size"]).decode().strip().split()
            )
            term_height, term_width = map(int, size_output)

            # Only use detected size if user didn't specify
            if not args.width:
                terminal_width = term_width
            if not args.height:
                terminal_height = term_height

        except (subprocess.SubprocessError, FileNotFoundError):
            # Fall back to defaults if that fails
            pass

    # Create a pyte screen and stream with the determined dimensions
    screen = pyte.Screen(terminal_width, terminal_height)
    stream = pyte.Stream(screen)

    # Configure screen options for better compatibility
    screen.set_mode(pyte.modes.LNM)  # Line feed/new line mode

    # Clear the screen
    print("\033[H\033[J", end="", flush=True)
    print(f"Terminal size: {terminal_width}x{terminal_height}")
    print(f"Running program: {args.program}")
    print(f"Using {'delta' if args.delta else 'full'} screen updates")

    # Run the specified program
    try:
        # Use pty to create a pseudo-terminal
        import fcntl
        import pty
        import struct
        import termios

        # Create a master/slave pty pair
        master_fd, slave_fd = pty.openpty()

        # Set the terminal size on the pty
        term_size = struct.pack("HHHH", terminal_height, terminal_width, 0, 0)
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, term_size)

        # Set environment variables to match the terminal size
        env = os.environ.copy()
        env["TERM"] = "xterm-256color"  # Good compatibility
        env["COLUMNS"] = str(terminal_width)
        env["LINES"] = str(terminal_height)

        # Split the command and args properly, handling quoted arguments
        if " " in args.program:
            import shlex

            cmd_parts = shlex.split(args.program)
        else:
            cmd_parts = args.program.split()

        # Start the process connected to our pty
        process = subprocess.Popen(
            cmd_parts,
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,
            env=env,
            start_new_session=True,
            close_fds=True,
        )

        # Close the slave side - it's now managed by the child process
        os.close(slave_fd)

        # Make master non-blocking for reading
        fl = fcntl.fcntl(master_fd, fcntl.F_GETFL)
        fcntl.fcntl(master_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        # Read loop
        while process.poll() is None:  # While process is running
            try:
                data = os.read(master_fd, 4096)
                if data:
                    text_data = data.decode("utf-8", errors="replace")
                    stream.feed(text_data)

                    # Display using either full screen or delta updates
                    if args.delta:
                        display_dirty_lines(screen)
                    else:
                        display_screen(screen)
                else:
                    time.sleep(0.01)  # Short sleep to prevent CPU hogging
            except (IOError, OSError) as e:
                if e.errno != errno.EAGAIN:  # Not "resource temporarily unavailable"
                    raise
                time.sleep(0.01)  # No data ready, short sleep

        # Process exited, read any remaining output
        try:
            while True:
                data = os.read(master_fd, 4096)
                if not data:
                    break
                text_data = data.decode("utf-8", errors="replace")
                stream.feed(text_data)

                # Display the final state
                if args.delta:
                    display_dirty_lines(screen)
                else:
                    display_screen(screen)
        except (IOError, OSError):
            pass

        # Clean up
        os.close(master_fd)

    except (KeyboardInterrupt, ImportError, OSError) as e:
        if isinstance(e, ImportError):
            print(f"Error: pty module not available - {e}")
        elif isinstance(e, OSError):
            print(f"\nError running program: {e}")
        else:
            print("\nProgram terminated")

    print("Done!")


if __name__ == "__main__":
    main()

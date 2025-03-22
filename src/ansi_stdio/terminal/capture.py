import errno
import fcntl
import os
import pty
import struct
import subprocess
import termios
import time
from typing import Callable, Optional

import pyte

from .info import get_terminal_size


def capture_terminal(
    program: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    buffer_size: int = 4096,
    display_callback: Optional[Callable[[pyte.Screen], None]] = None,
) -> pyte.Screen:
    """
    Capture terminal output for a given program with flexible processing.

    Args:
        program (str): Command to run in the terminal
        width (int, optional): Terminal width. Defaults to detected width.
        height (int, optional): Terminal height. Defaults to detected height.
        buffer_size (int, optional): Size of read buffer. Defaults to 4096.
        display_callback (Callable, optional): Function to process screen state.
            Receives the pyte Screen object for custom handling.

    Returns:
        pyte.Screen: The final screen state after program execution
    """

    # Determine terminal dimensions
    if width is None or height is None:
        detected_width, detected_height = get_terminal_size()
        width = width or detected_width
        height = height or detected_height

    # Create pyte screen and stream
    screen = pyte.Screen(width, height)
    stream = pyte.Stream(screen)

    # Configure screen options
    screen.set_mode(pyte.modes.LNM)  # Line feed/new line mode

    # Prepare program execution
    try:
        # Create a master/slave pty pair
        master_fd, slave_fd = pty.openpty()

        # Set the terminal size on the pty
        term_size = struct.pack("HHHH", height, width, 0, 0)
        fcntl.ioctl(slave_fd, termios.TIOCSWINSZ, term_size)

        # Prepare environment
        env = os.environ.copy()
        env["TERM"] = "xterm-256color"
        env["COLUMNS"] = str(width)
        env["LINES"] = str(height)

        # Split program command, handling quoted arguments
        try:
            import shlex

            cmd_parts = shlex.split(program) if " " in program else program.split()
        except ImportError:
            cmd_parts = program.split()

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

        # Close the slave side
        os.close(slave_fd)

        # Make master non-blocking for reading
        fl = fcntl.fcntl(master_fd, fcntl.F_GETFL)
        fcntl.fcntl(master_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

        # Read loop
        while process.poll() is None:  # While process is running
            try:
                data = os.read(master_fd, buffer_size)
                if data:
                    text_data = data.decode("utf-8", errors="replace")
                    stream.feed(text_data)

                    # Call display callback if provided
                    if display_callback:
                        display_callback(screen)
                else:
                    time.sleep(0.01)  # Short sleep to prevent CPU hogging
            except (IOError, OSError) as e:
                if e.errno != errno.EAGAIN:  # Not "resource temporarily unavailable"
                    raise
                time.sleep(0.01)  # No data ready, short sleep

        # Process exited, read any remaining output
        try:
            while True:
                data = os.read(master_fd, buffer_size)
                if not data:
                    break
                text_data = data.decode("utf-8", errors="replace")
                stream.feed(text_data)

                # Final display callback
                if display_callback:
                    display_callback(screen)
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

    return screen

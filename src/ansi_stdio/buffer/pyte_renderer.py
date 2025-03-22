"""
Pyte screen renderer for ANSI stdio.
Converts pyte screen state to formatted strings with ANSI escape sequences.
"""

# Build color maps once at module import
FG_COLORS = {
    "black": "30",
    "red": "31",
    "green": "32",
    "yellow": "33",
    "blue": "34",
    "magenta": "35",
    "cyan": "36",
    "white": "37",
    "brightblack": "90",
    "brightred": "91",
    "brightgreen": "92",
    "brightyellow": "93",
    "brightblue": "94",
    "brightmagenta": "95",
    "brightcyan": "96",
    "brightwhite": "97",
}

BG_COLORS = {
    "black": "40",
    "red": "41",
    "green": "42",
    "yellow": "43",
    "blue": "44",
    "magenta": "45",
    "cyan": "46",
    "white": "47",
    "brightblack": "100",
    "brightred": "101",
    "brightgreen": "102",
    "brightyellow": "103",
    "brightblue": "104",
    "brightmagenta": "105",
    "brightcyan": "106",
    "brightwhite": "107",
}

# Try importing pyte's graphics if available
try:
    from pyte import graphics

    if hasattr(graphics, "FG"):
        FG_COLORS.update({k.lower(): v for k, v in graphics.FG.items()})
    if hasattr(graphics, "BG"):
        BG_COLORS.update({k.lower(): v for k, v in graphics.BG.items()})
except (ImportError, AttributeError):
    pass


def format_char(char):
    """
    Format a single character with its attributes.

    Args:
        char: A pyte character with attributes

    Returns:
        str: The formatted character with ANSI codes
    """
    # Build ANSI style codes
    codes = []

    # Text attributes
    if char.bold:
        codes.append("1")
    if char.italics:
        codes.append("3")
    if char.underscore:
        codes.append("4")
    if char.blink:
        codes.append("5")
    if char.reverse:
        codes.append("7")

    # Foreground color
    if char.fg != "default":
        # Get the closest ANSI color code
        fg_code = "39"  # Default foreground

        if isinstance(char.fg, str):
            color_name = char.fg.lower()
            fg_code = FG_COLORS.get(color_name, "39")
        elif isinstance(char.fg, int):
            # Assume it's a direct color index
            fg_code = str(30 + (char.fg % 8))

        codes.append(fg_code)

    # Background color
    if char.bg != "default":
        # Get the closest ANSI color code
        bg_code = "49"  # Default background

        if isinstance(char.bg, str):
            color_name = char.bg.lower()
            bg_code = BG_COLORS.get(color_name, "49")
        elif isinstance(char.bg, int):
            # Assume it's a direct color index
            bg_code = str(40 + (char.bg % 8))

        codes.append(bg_code)

    # Construct full ANSI code if we have any style attributes
    if codes:
        return f"\033[{';'.join(codes)}m{char.data}\033[0m"
    else:
        return char.data


def format_line(row, width):
    """
    Format a single line of the screen.

    Args:
        row: A dictionary of column -> character mappings
        width: The width of the screen

    Returns:
        str: The formatted line
    """
    line = []

    # Build the line character by character
    for x in range(width):
        if x in row and row[x].data:
            line.append(format_char(row[x]))
        else:
            # Empty cell
            line.append(" ")

    return "".join(line)


def render_screen(screen):
    """
    Convert a pyte screen to a list of formatted strings.

    Args:
        screen: A pyte.Screen instance

    Returns:
        list: A list of strings containing ANSI-formatted text, one per line
    """
    width = screen.columns
    height = screen.lines

    # List to hold formatted lines
    formatted_lines = []

    # Build the screen line by line
    for y in range(height):
        if y in screen.buffer:
            formatted_lines.append(format_line(screen.buffer[y], width))
        else:
            # Empty line
            formatted_lines.append(" " * width)

    return formatted_lines


def render_dirty_lines(screen, clear_dirty=True):
    """
    Convert only dirty lines of a pyte screen to formatted strings.

    Args:
        screen: A pyte.Screen instance
        clear_dirty: Whether to clear the dirty set after processing

    Returns:
        dict: A dictionary mapping line numbers to formatted strings
    """
    width = screen.columns

    # Dictionary to hold dirty lines
    dirty_lines = {}

    # Process only dirty lines
    for y in screen.dirty:
        if y in screen.buffer:
            dirty_lines[y] = format_line(screen.buffer[y], width)

    # Clear the dirty set if requested
    if clear_dirty:
        screen.dirty.clear()

    return dirty_lines


def display_screen(screen):
    """
    Display a pyte screen using ANSI escape sequences.

    Args:
        screen: A pyte.Screen instance
    """
    # Start fresh - move to home position and clear screen
    print("\033[H\033[J", end="", flush=True)

    # Get formatted lines
    formatted_lines = render_screen(screen)

    # Print each line
    for line in formatted_lines:
        print(line, end="\r\n", flush=True)


def display_dirty_lines(screen, clear_dirty=True):
    """
    Display only the dirty lines of a pyte screen.

    Args:
        screen: A pyte.Screen instance
        clear_dirty: Whether to clear the dirty set after processing
    """
    # Get formatted dirty lines
    dirty_lines = render_dirty_lines(screen, clear_dirty)

    # Print each dirty line with proper cursor positioning
    for y, line in dirty_lines.items():
        # Position cursor at the start of the line
        print(f"\033[{y+1};1H{line}", end="", flush=True)

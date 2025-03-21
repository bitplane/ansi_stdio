from rich.segment import Segment


class Buffer:
    """
    A 2D sparse grid of rich Segments
    """

    def __init__(self):
        """
        Initialize the buffer as a sparse structure.
        """
        self.data = {}  # {y: {x: segment}}
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0  # exclusive
        self.max_y = 0  # exclusive

    def __getitem__(self, coords):
        """
        Get the item at the given coordinates.

        Args:
            coords: A tuple of (x, y) coordinates

        Returns:
            The Segment at those coordinates or None if empty
        """
        x, y = coords
        return self.data.get(y, {}).get(x)

    def __setitem__(self, coords, segment):
        """
        Set a segment at the given coordinates.

        Args:
            coords: A tuple of (x, y) coordinates
            segment: The Segment to place at these coordinates
        """
        x, y = coords
        self.set(x, y, segment)

    def set(self, x, y, segment):
        """
        Set cell(s) starting at given coordinates with a Segment.
        Handles multi-character segments by writing each character in sequence.

        Args:
            x: Starting X coordinate
            y: Y coordinate
            segment: Rich Segment object to place at this position
        """

        if not self.width:
            self.min_x, self.max_x = x, x + len(segment.text)
            self.min_y, self.max_y = y, y + 1
        else:
            self.min_x = min(self.min_x, x)
            self.min_y = min(self.min_y, y)
            self.max_x = max(self.max_x, x + len(segment.text))
            self.max_y = max(self.max_y, y + 1)

        # Ensure y entry exists before loop
        if not self.data.get(y):
            self.data[y] = {}

        # Handle multi-character segments by writing each char
        style = segment.style
        for i, char in enumerate(segment.text):
            # Store a new single-character segment
            self.data[y][x + i] = Segment(char, style)

    @property
    def bounds(self):
        """
        Returns the bounding box of content as (min_x, min_y, max_x, max_y).
        Max values are exclusive (Python slice-style).
        """
        return (self.min_x, self.min_y, self.max_x, self.max_y)

    @property
    def width(self):
        """Width of the content"""
        return self.max_x - self.min_x

    @property
    def height(self):
        """Height of the content"""
        return self.max_y - self.min_y

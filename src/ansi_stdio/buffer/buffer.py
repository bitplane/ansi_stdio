from rich.segment import Segment

from ..bounds import Bounds


class Buffer:
    """
    A 2D sparse grid of rich.Segment objects.
    """

    def __init__(self):
        """
        Initialize the buffer as a sparse structure.
        """
        self.data = {}  # {y: {x: segment}}
        self.bounds = Bounds()

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

        self.bounds.update(x, y)
        txtlen = len(segment.text)
        if txtlen > 1:
            self.bounds.update(x - 1 + txtlen, y)

        # Ensure y entry exists before loop
        if not self.data.get(y):
            self.data[y] = {}

        # Handle multi-character segments by writing each char
        style = segment.style
        for i, char in enumerate(segment.text):
            # Store a new single-character segment
            self.data[y][x + i] = Segment(char, style)

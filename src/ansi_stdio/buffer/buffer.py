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
        self._size = 0

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

    def __iadd__(self, other) -> "Buffer":
        """
        Merge another buffer into this one.
        """
        if not isinstance(other, Buffer):
            raise TypeError(f"Cannot merge {type(other)} with Buffer")

        # Update bounds in one operation
        self.bounds += other.bounds

        # Merge the data from the other buffer
        for y, row in other.data.items():
            if y not in self.data:
                # Fast path: copy entire row if it doesn't exist in current buffer
                self.data[y] = row.copy()
            else:
                # Update existing row
                self.data[y].update(row)

        self.compute_size()

        return self

    def __add__(self, other) -> "Buffer":
        """
        Create a new buffer by merging this buffer with another.
        """
        result = self.copy()
        result += other
        return result

    def __and__(self, bounds: Bounds) -> "Buffer":
        """
        Crop the buffer to the given bounds.
        Returns a newly allocated buffer.
        """
        result = Buffer()
        for y in range(bounds.min_y, bounds.max_y):
            row = self.data.get(y)
            if not row:
                continue
            for x in range(bounds.min_x, bounds.max_x):
                if x in row:
                    result.set(x, y, row[x])
        return result

    def __iand__(self, bounds: Bounds) -> "Buffer":
        """
        Crop the buffer to the given bounds.
        This modifies the buffer in place.
        """
        self.data = (self & bounds).data
        self.bounds = bounds
        self.recalculate(bounds=False)

        return self

    def __len__(self):
        """
        Get the number of cells set in the buffer.
        """
        return self._size

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
            if x + i not in self.data[y]:
                self._size += 1
            # Store a new single-character segment
            self.data[y][x + i] = Segment(char, style)

    def copy(self):
        """
        Create a deep copy of this buffer.

        Returns:
            A new Buffer instance with the same content
        """
        new_buffer = Buffer()

        # Copy the bounds
        new_buffer.bounds = Bounds(
            self.bounds.min_x, self.bounds.min_y, self.bounds.max_x, self.bounds.max_y
        )

        # Copy the data structure
        for y, row in self.data.items():
            new_buffer.data[y] = row.copy()

        return new_buffer

    def recalculate(self, size: bool = True, bounds: bool = True):
        """
        Recalculate the size and bounds
        """
        if size:
            self._size = sum(len(row) for row in self.data.values())

        if bounds:
            self.bounds.reset()
            for y, row in self.data.items():
                for x in row:
                    self.bounds.update(x, y)

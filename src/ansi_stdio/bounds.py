class Bounds:
    """
    Represents a rectangular area on the screen.
    """

    def __init__(self, min_x=0, min_y=0, max_x=0, max_y=0):
        """
        Initialize the bounds with the given coordinates.
        """
        self.min_x = min_x
        self.min_y = min_y
        self.max_x = max_x
        self.max_y = max_y

    def reset(self):
        """
        Reset the bounds to the origin.
        """
        self.min_x = 0
        self.min_y = 0
        self.max_x = 0
        self.max_y = 0

    def __add__(self, other):
        """
        Combine two bounds into a new bounds that encompasses both.
        """
        if not self:
            return other
        if not other:
            return self
        return Bounds(
            min_x=min(self.min_x, other.min_x),
            min_y=min(self.min_y, other.min_y),
            max_x=max(self.max_x, other.max_x),
            max_y=max(self.max_y, other.max_y),
        )

    def __bool__(self):
        """
        True if the bounds have a non-zero area.
        """
        return (self.min_x != self.max_x) or (self.min_y != self.max_y)

    def update(self, x, y):
        """
        Update the bounds to include the given coordinates.
        """
        if not self:
            self.min_x, self.max_x = x, x + 1
            self.min_y, self.max_y = y, y + 1
        else:
            self.min_x = min(self.min_x, x)
            self.min_y = min(self.min_y, y)
            self.max_x = max(self.max_x, x + 1)
            self.max_y = max(self.max_y, y + 1)

    @property
    def width(self):
        """
        Width of the bounding box.
        """
        return self.max_x - self.min_x

    @property
    def height(self):
        """
        Height of the bounding box.
        """
        return self.max_y - self.min_y

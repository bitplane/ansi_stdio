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
        # make sure it's not inside out
        self.max_x = max(min_x, max_x)
        self.max_y = max(min_y, max_y)

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

    def __and__(self, other: "Bounds") -> "Bounds":
        """
        Intersect two bounds to find the overlapping area.
        """
        if not self or not other:
            return Bounds()

        return Bounds(
            max(self.min_x, other.min_x),
            max(self.min_y, other.min_y),
            min(self.max_x, other.max_x),
            min(self.max_y, other.max_y),
        )

    def __iand__(self, other: "Bounds") -> "Bounds":
        """
        Crop the bounds to the overlapping area.
        """
        result = self & other
        self.min_x, self.min_y = result.min_x, result.min_y
        self.max_x, self.max_y = result.max_x, result.max_y
        return self

    def __bool__(self):
        """
        True if the bounds have a non-zero area.
        """
        return (self.min_x != self.max_x) or (self.min_y != self.max_y)

    def __len__(self):
        """
        Return the area of the bounds.
        """
        return self.width * self.height

    def __contains__(self, item):
        """
        Check if the given item is contained within the bounds.
        """
        if isinstance(item, tuple) and len(item) == 2:
            return self.contains(x=item[0], y=item[1])

        if isinstance(item, Bounds):
            if not item:
                # The empty set is a subset of everything
                return True
            return (
                self.min_x <= item.min_x
                and item.max_x <= self.max_x
                and self.min_y <= item.min_y
                and item.max_y <= self.max_y
            )

        if hasattr(item, "bounds"):
            return item.bounds in self

        raise TypeError(f"Cannot check containment for {type(item)}")

    def __eq__(self, other):
        if not isinstance(other, Bounds):
            return NotImplemented
        return (
            self.min_x == other.min_x
            and self.min_y == other.min_y
            and self.max_x == other.max_x
            and self.max_y == other.max_y
        )

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

    def contains(self, x=None, y=None):
        """
        Check if the given coordinates are within the bounds.
        If x or y is None, it will not be checked.
        """
        if x is not None and not (self.min_x <= x < self.max_x):
            return False
        if y is not None and not (self.min_y <= y < self.max_y):
            return False

        return True

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

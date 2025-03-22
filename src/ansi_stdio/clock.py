from time import time


class Clock:
    """
    Base class for clocks.

    A clock represents a time transformation that can be applied to animations.
    Each clock can have a parent clock, creating a hierarchy of time transformations.
    """

    def __init__(self, parent=None):
        """
        Initialize the clock.

        Args:
            parent: Optional parent clock that feeds time to this clock
        """
        self.parent = parent  # parent clock
        self.paused = False  # is the clock paused?
        self.skew = 0.0  # skew from parent clock
        self.paused_at = None  # time when paused

    @property
    def time(self):
        """
        Get the current time, considering parent's time and local adjustments.

        Returns:
            Current transformed time in seconds
        """
        if self.paused:
            return self.paused_at

        return self.parent_time + self.skew

    @time.setter
    def time(self, value):
        """
        Set the current time by adjusting the skew from parent.

        Args:
            value: The time to set
        """
        if self.paused:
            # When paused, just update the paused_at value
            self.paused_at = value
        else:
            # When running, adjust the skew
            parent_time = self.parent_time
            self.skew = value - parent_time

    @property
    def parent_time(self):
        """
        Get the time of the parent clock, or system time if no parent.

        Returns:
            Parent's time or system time in seconds
        """
        return self.parent.time if self.parent else time()

    def pause(self):
        """
        Pause the clock, freezing its time.
        """
        if self.paused:
            return
        self.paused_at = self.time
        self.paused = True

    def resume(self):
        """
        Resume the clock, continuing from where it was paused.
        Adjusts the skew to account for time passed while paused.
        """
        if not self.paused:
            return
        self.skew += self.paused_at - self.parent_time
        self.paused = False
        self.paused_at = None


# Default wall clock instance
wall = Clock()

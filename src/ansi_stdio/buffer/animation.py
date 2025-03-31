from bisect import bisect_right

from ansi_stdio.buffer.buffer import Buffer
from ansi_stdio.buffer.frame import DeltaFrame, Frame
from ansi_stdio.core.versioned import Versioned, changes, waits


class Animation(Versioned):
    """
    An animation that we can render somewhere.
    """

    def __init__(self):
        super().__init__()
        self._frames: list[Frame] = []
        self._cache: dict[tuple, Buffer] = {}

    @property
    def frames(self) -> list[Frame]:
        return self._frames

    @changes
    def add(self, frame: Frame):
        if self._frames:
            frame.parent = self._frames[-1]
        self._frames.append(frame)

    @waits
    def render(self, t: float) -> Buffer:
        if not self._frames:
            return Buffer()

        times = [f.time for f in self._frames]
        index = bisect_right(times, t) - 1
        if index < 0:
            return Buffer()

        key = []
        buffer = None

        for frame in self._frames[index:]:
            if frame.time > t:
                break

            key.append(frame.cache_key)

            if not isinstance(frame, DeltaFrame):
                buffer = frame.buffer.copy()
            else:
                buffer += frame.buffer

        cache_key = tuple(key)
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        self._cache[cache_key] = buffer.copy()
        return buffer

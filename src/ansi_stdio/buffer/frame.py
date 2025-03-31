from __future__ import annotations

from typing import Optional

from ansi_stdio.buffer.buffer import Buffer  # adjust if location differs
from ansi_stdio.core.versioned import Versioned, changes


class Frame(Versioned):
    """
    A frame of animation, containing a buffer.
    """

    def __init__(
        self, buffer: Buffer, duration: float = 0.1, parent: Optional[Frame] = None
    ):
        super().__init__()
        self._buffer: Buffer = buffer
        self._duration: float = duration
        self._time: float = 0.0
        self._parent: Optional[Frame] = parent
        self._child: Optional[Frame] = None
        if parent:
            parent._child = self
            self._time = parent.time + parent.duration

    @property
    def buffer(self) -> Buffer:
        return self._buffer

    @buffer.setter
    @changes
    def buffer(self, value: Buffer):
        self._buffer = value

    @property
    def duration(self) -> float:
        return self._duration

    @duration.setter
    @changes
    def duration(self, value: float):
        self._duration = value
        self._update_timing()

    @property
    def time(self) -> float:
        return self._time

    @property
    def parent(self) -> Optional[Frame]:
        return self._parent

    @parent.setter
    @changes
    def parent(self, frame: Optional[Frame]):
        self._parent = frame
        if frame:
            frame._child = self
        self._update_timing()

    @property
    def child(self) -> Optional[Frame]:
        return self._child

    def _update_timing(self):
        if self._parent:
            self._time = self._parent.time + self._parent.duration
        else:
            self._time = 0.0
        if self._child:
            self._child._update_timing()

    def __hash__(self) -> int:
        return hash(
            (
                id(self.parent),
                self.parent.version if self.parent else 0,
                id(self),
                self.version,
            )
        )


class KeyFrame(Frame):
    pass


class DeltaFrame(Frame):
    def __init__(
        self, buffer: Buffer, duration: float = 0.1, parent: Optional[Frame] = None
    ):
        super().__init__(buffer, duration, parent)
        self.parent = parent

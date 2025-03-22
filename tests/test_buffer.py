from rich.segment import Segment

from ansi_stdio.buffer.buffer import Buffer


def test_create_buffer():
    buffer = Buffer()
    assert buffer is not None


def test_get_empty():
    buffer = Buffer()
    segment = buffer[0, 0]
    assert segment is None


def test_set_segment():
    buffer = Buffer()
    buffer[0, 0] = Segment("hello")


def test_get_segment():
    buffer = Buffer()
    buffer[0, 0] = Segment("hello")

    assert buffer[0, 0].text == "h"
    assert buffer[1, 0].text == "e"
    assert buffer[2, 0].text == "l"
    assert buffer[3, 0].text == "l"
    assert buffer[4, 0].text == "o"


def test_bounds():
    buffer = Buffer()
    buffer[-1, 5] = Segment("hello")

    assert buffer.bounds.min_x == -1
    assert buffer.bounds.min_y == 5
    assert buffer.bounds.max_x == 4
    assert buffer.bounds.max_y == 6

    assert buffer.bounds.width == 5
    assert buffer.bounds.height == 1

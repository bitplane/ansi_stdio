from rich.segment import Segment

from ansi_stdio.buffer import Buffer


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

    assert buffer.bounds == (-1, 5, 4, 6)


def test_width():
    buffer = Buffer()
    buffer[50, 50] = Segment("bleh")
    buffer[100, 100] = Segment("bleh")

    assert buffer.width == 54


def test_height():
    buffer = Buffer()
    buffer[-10, 10] = Segment(".")
    buffer[-2, 20] = Segment(".")

    assert buffer.height == 11

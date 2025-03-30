from rich.segment import Segment

from ansi_stdio.bounds import Bounds
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


def test_set_and_get_single_char():
    buf = Buffer()
    buf[2, 3] = Segment("X")

    assert buf[2, 3].text == "X"
    assert buf[1, 3] is None
    assert buf.bounds.contains(2, 3)
    assert len(buf) == 1


def test_set_multi_char_segment():
    buf = Buffer()
    buf[5, 5] = Segment("ABC", style="bold")

    assert buf[5, 5].text == "A"
    assert buf[6, 5].text == "B"
    assert buf[7, 5].text == "C"
    assert len(buf) == 3


def test_buffer_addition():
    a = Buffer()
    b = Buffer()

    a[0, 0] = Segment("X")
    b[1, 0] = Segment("Y")

    c = a + b
    assert c[0, 0].text == "X"
    assert c[1, 0].text == "Y"
    assert len(c) == 2
    assert len(a) == 1
    assert len(b) == 1


def test_buffer_iadd_merges():
    a = Buffer()
    b = Buffer()

    a[0, 0] = Segment("X")
    b[1, 0] = Segment("Y")

    a += b
    assert a[0, 0].text == "X"
    assert a[1, 0].text == "Y"
    assert len(a) == 2


def test_crop_and():
    buf = Buffer()
    buf[1, 1] = Segment("A")
    buf[5, 5] = Segment("B")

    cropped = buf & Bounds(0, 0, 3, 3)
    assert cropped[1, 1].text == "A"
    assert cropped[5, 5] is None
    assert len(cropped) == 1


def test_crop_iand_inplace():
    buf = Buffer()
    buf[1, 1] = Segment("A")
    buf[5, 5] = Segment("B")

    buf &= Bounds(0, 0, 3, 3)
    assert buf[1, 1].text == "A"
    assert buf[5, 5] is None
    assert len(buf) == 1


def test_copy_isolated():
    buf = Buffer()
    buf[0, 0] = Segment("Z")

    c = buf.copy()
    c[1, 0] = Segment("Q")

    assert buf[1, 0] is None
    assert c[0, 0].text == "Z"
    assert c[1, 0].text == "Q"


def test_recalculate_size_and_bounds():
    buf = Buffer()
    buf[3, 4] = Segment("X")
    buf[1, 2] = Segment("Y")

    # Break it manually
    buf.data[10] = {20: Segment("!" * 3)}  # Should add 3

    buf.recalculate()

    assert buf.bounds.contains(1, 2)
    assert buf.bounds.contains(20, 10)
    assert len(buf) == 1 + 1 + 3  # 2 originals + 3 new chars

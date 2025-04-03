import pytest
from rich.segment import Segment

from ansi_stdio.buffer.buffer import Buffer
from ansi_stdio.core.box import Box


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


def test_box():
    buffer = Buffer()
    buffer[-1, 5] = Segment("hello")

    assert buffer.box.min_x == -1
    assert buffer.box.min_y == 5
    assert buffer.box.max_x == 4
    assert buffer.box.max_y == 6

    assert buffer.box.width == 5
    assert buffer.box.height == 1


def test_set_and_get_single_char():
    buf = Buffer()
    buf[2, 3] = Segment("X")

    assert buf[2, 3].text == "X"
    assert buf[1, 3] is None
    assert buf.box.contains(2, 3)
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

    cropped = buf & Box(0, 0, 3, 3)
    assert cropped[1, 1].text == "A"
    assert cropped[5, 5] is None
    assert len(cropped) == 1


def test_crop_iand_inplace():
    buf = Buffer()
    buf[1, 1] = Segment("A")
    buf[5, 5] = Segment("B")

    buf &= Box(0, 0, 3, 3)
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


def test_recalculate_size_and_box():
    buf = Buffer()
    buf[3, 4] = Segment("X")
    buf[1, 2] = Segment("Y")

    # Break it manually
    buf._data[10] = {i: Segment("!") for i in range(20, 23)}

    buf.recalculate()

    assert buf.box.contains(1, 2)
    assert buf.box.contains(20, 10)
    assert len(buf) == 1 + 1 + 3  # 2 originals + 3 new chars


def test_buffer_iadd_fast_path_copy():
    src = Buffer()
    src[0, 0] = Segment("A")
    src[1, 0] = Segment("B")

    dst = Buffer()
    dst += src

    # The row should be copied wholesale
    assert 0 in dst._data
    assert dst[0, 0].text == "A"
    assert dst[1, 0].text == "B"

    # Should not share row object (deep copy)
    assert dst._data[0] is not src._data[0]


def test_buffer_iadd_type_error():
    buf = Buffer()

    with pytest.raises(TypeError):
        buf += "not a buffer"

    with pytest.raises(TypeError):
        buf += 123

    class Fake:
        pass

    with pytest.raises(TypeError):
        buf += Fake()


def test_buffer_iadd_merge_existing_row():
    a = Buffer()
    a[1, 1] = Segment("A")

    b = Buffer()
    b[2, 1] = Segment("B")  # same row (y=1), different x

    a += b
    assert a[1, 1].text == "A"
    assert a[2, 1].text == "B"


def test_buffer_sub_basic_diff():
    a = Buffer()
    b = Buffer()

    a[1, 1] = Segment("A")
    a[2, 1] = Segment("B")

    b[1, 1] = Segment("A")  # Same at (1,1), different at (2,1)

    diff = a - b

    assert diff[1, 1] is None
    assert diff[2, 1].text == "B"
    assert len(diff) == 1


def test_buffer_sub_all_same_is_empty():
    a = Buffer()
    b = Buffer()

    a[0, 0] = Segment("X")
    b[0, 0] = Segment("X")

    diff = a - b
    assert len(diff) == 0
    assert not diff._data  # Internal data should be empty


def test_buffer_sub_extra_in_b():
    a = Buffer()
    b = Buffer()

    b[0, 0] = Segment("Z")  # Only in b

    diff = a - b
    assert len(diff) == 0
    assert diff[0, 0] is None


def test_buffer_isub_in_place_removal():
    a = Buffer()
    b = Buffer()

    a[1, 1] = Segment("A")
    a[2, 1] = Segment("B")
    b[1, 1] = Segment("A")  # same

    a -= b
    assert a[1, 1] is None
    assert a[2, 1].text == "B"
    assert len(a) == 1


def test_buffer_isub_removes_empty_rows():
    a = Buffer()
    b = Buffer()

    a[1, 1] = Segment("A")
    b[1, 1] = Segment("A")

    assert 1 in a._data
    a -= b
    assert 1 not in a._data
    assert len(a) == 0

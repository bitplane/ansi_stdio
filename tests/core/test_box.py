import pytest

from ansi_stdio.core.box import Box


def test_create_box():
    box = Box()
    assert box is not None


def test_box_falsey():
    box = Box()
    assert not box


def test_box_truthy():
    box = Box(1, 1, 2, 2)
    assert box


def test_width():
    box = Box(-10, 10, 20, 20)
    assert box.width == 30


def test_height():
    box = Box(-10, 10, 20, 20)
    assert box.height == 10


def test_point_containment():
    b = Box(0, 0, 10, 10)

    assert (5, 5) in b
    assert (0, 0) in b
    assert (9, 9) in b
    assert (10, 10) not in b
    assert (-1, 5) not in b
    assert (5, 10) not in b


def test_axis_contains():
    b = Box(1, 2, 5, 6)

    assert b.contains(x=1)
    assert b.contains(x=4)
    assert not b.contains(x=0)
    assert not b.contains(x=5)

    assert b.contains(y=2)
    assert b.contains(y=5)
    assert not b.contains(y=1)
    assert not b.contains(y=6)

    assert b.contains(x=2, y=3)
    assert not b.contains(x=0, y=3)
    assert not b.contains(x=2, y=7)


def test_partial_tuple_containment():
    b = Box(10, 20, 50, 60)

    assert (None, 25) in b  # y only
    assert (25, None) in b  # x only
    assert (None, 100) not in b
    assert (5, None) not in b
    assert (None, None) in b  # vacuously contained


def test_box_in_box():
    outer = Box(0, 0, 10, 10)
    inner = Box(2, 2, 5, 5)

    assert inner in outer
    assert outer in outer
    assert outer not in inner

    assert Box() in outer  # empty box subset of everything


def test_box_update_and_len():
    b = Box()
    assert not b
    assert len(b) == 0

    b.update(3, 5)
    assert b.contains(3, 5)
    assert len(b) == 1
    assert b.width == 1
    assert b.height == 1


def test_box_addition_union():
    a = Box(0, 0, 5, 5)
    b = Box(4, 4, 10, 10)
    result = a + b

    assert result.min_x == 0
    assert result.min_y == 0
    assert result.max_x == 10
    assert result.max_y == 10
    assert (9, 9) in result


def test_box_intersection():
    a = Box(0, 0, 5, 5)
    b = Box(3, 3, 10, 10)
    result = a & b

    assert result.min_x == 3
    assert result.min_y == 3
    assert result.max_x == 5
    assert result.max_y == 5
    assert (4, 4) in result
    assert (2, 2) not in result

    empty = a & Box(6, 6, 7, 7)
    assert not empty
    assert len(empty) == 0


def test_iand_in_place():
    b = Box(0, 0, 10, 10)
    b &= Box(3, 3, 7, 7)
    assert b.min_x == 3
    assert b.min_y == 3
    assert b.max_x == 7
    assert b.max_y == 7


def test_box_reset():
    b = Box(1, 2, 3, 4)
    b.reset()
    assert b.min_x == 0
    assert b.min_y == 0
    assert b.max_x == 0
    assert b.max_y == 0
    assert not b
    assert len(b) == 0


def test_box_add_with_empty():
    a = Box(1, 1, 3, 3)
    b = Box()  # empty

    result1 = a + b
    result2 = b + a

    # Addition should return the non-empty one
    assert result1.min_x == 1
    assert result1.max_x == 3
    assert result2.min_y == 1
    assert result2.max_y == 3


def test_box_and_with_empty():
    a = Box(0, 0, 5, 5)
    b = Box()  # empty

    result1 = a & b
    result2 = b & a

    assert not result1
    assert not result2
    assert len(result1) == 0
    assert len(result2) == 0


def test_box_contains_box_attribute():
    class Dummy:
        def __init__(self, box):
            self.box = box

    outer = Box(0, 0, 10, 10)
    inner = Box(2, 2, 4, 4)
    wrapper = Dummy(inner)

    assert wrapper in outer

    outer2 = Box(0, 0, 3, 3)
    wrapper2 = Dummy(Box(2, 2, 6, 6))

    assert wrapper2 not in outer2


def test_box_contains_invalid_type():
    b = Box(0, 0, 5, 5)

    with pytest.raises(TypeError):
        _ = "not a box" in b


def test_box_equality():
    a = Box(1, 2, 5, 6)
    b = Box(1, 2, 5, 6)
    c = Box(0, 0, 5, 6)

    assert a == b
    assert a != c
    assert a != (1, 2, 5, 6)  # different type

    # sanity check symmetry
    assert not (b != a)

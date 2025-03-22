from ansi_stdio.bounds import Bounds


def test_create_bounds():
    bounds = Bounds()
    assert bounds is not None


def test_bounds_falsey():
    bounds = Bounds()
    assert not bounds


def test_bounds_truthy():
    bounds = Bounds(1, 1, 2, 2)
    assert bounds


def test_width():
    bounds = Bounds(-10, 10, 20, 20)
    assert bounds.width == 30


def test_height():
    bounds = Bounds(-10, 10, 20, 20)
    assert bounds.height == 10

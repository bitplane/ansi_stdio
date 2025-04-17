import pytest

from ansi_stdio.core.saved import CLASSES, Param, Params, Saved


def test_init_subclass_registers_class():
    class MyThing(Saved):
        def __init__(self, a: int, b: str = "default"):
            self.a = a
            self.b = b

    # Check class is registered
    assert "MyThing" in CLASSES
    entry = CLASSES["MyThing"]
    assert isinstance(entry, Params)
    assert entry.type is MyThing
    assert entry.params["a"] == Param(type=int, default=None)
    assert entry.params["b"] == Param(type=str, default="default")
    # ensure the class gets its params too for introspection
    assert MyThing.params["a"] == Param(type=int, default=None)
    assert MyThing.params["b"] == Param(type=str, default="default")


def test_duplicate_class_raises():
    class Unique(Saved):
        def __init__(self, x: int):
            pass

    with pytest.raises(ValueError):

        class Unique(Saved):  # noqa: F811 - intentional redefinition
            def __init__(self, x: int):
                pass


def test_init_subclass_no_args():
    class NoArgs(Saved):
        def __init__(self):
            pass

    # Check class is registered
    assert "NoArgs" in CLASSES
    entry = CLASSES["NoArgs"]
    assert isinstance(entry, Params)
    assert entry.type is NoArgs
    assert entry.params == {}


class Point(Saved):
    def __init__(self, x: int, y: int = 0):
        self.x = x
        self.y = y


class Label(Saved):
    def __init__(self, text: str, pos: Point = Point(0, 0)):
        self.text = text
        self.pos = pos


def test_init_subclass_registration():
    assert "Point" in CLASSES
    assert "Label" in CLASSES
    assert CLASSES["Point"].params["x"].type == int
    assert CLASSES["Point"].params["y"].default == 0


def test_arguments_filters_defaults():
    p = Point(10, 0)  # y is default
    args = p.arguments()
    assert args == {"x": 10}


def test_arguments_includes_nondefaults():
    p = Point(10, 5)  # y is not default
    args = p.arguments()
    assert args == {"x": 10, "y": 5}


def test_nested_serialization():
    lbl = Label("Test", Point(1, 2))
    js = lbl.save()
    assert js["text"] == "Test"
    assert js["pos"]["x"] == 1
    assert js["pos"]["y"] == 2


def test_class_params_exposed():
    assert set(Label.params.keys()) == {"text", "pos"}
    assert Label.params["text"].type == str
    assert Label.params["pos"].type == Point


def test_class_name_serialized():
    lbl = Label("Test", Point(1, 2))
    js = lbl.save()
    assert js["class"] == "Label"

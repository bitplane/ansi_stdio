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

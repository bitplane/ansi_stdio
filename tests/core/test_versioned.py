from ansi_stdio.core.versioned import Versioned, changes, waits


def test_version_starts_at_zero():
    v = Versioned()
    assert v.version == 0


def test_change_increments_version():
    v = Versioned()
    v.change()
    assert v.version == 1
    v.change()
    assert v.version == 2


def test_changes_decorator_increments_version():
    class Demo(Versioned):
        @changes
        def mutate(self):
            return "done"

    d = Demo()
    assert d.version == 0
    result = d.mutate()
    assert result == "done"
    assert d.version == 1
    d.mutate()
    assert d.version == 2


def test_waits_decorator_does_not_increment_version():
    class Demo(Versioned):
        @waits
        def readonly(self):
            return "safe"

    d = Demo()
    d.change()
    assert d.version == 1
    result = d.readonly()
    assert result == "safe"
    assert d.version == 1  # unchanged


def test_mixed_changes_and_waits():
    class Demo(Versioned):
        @changes
        def mutate(self):
            return "mutate"

        @waits
        def readonly(self):
            return "readonly"

    d = Demo()
    assert d.version == 0
    d.readonly()
    assert d.version == 0
    d.mutate()
    assert d.version == 1

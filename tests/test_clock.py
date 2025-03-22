from time import sleep
from unittest.mock import patch

from ansi_stdio.clock import Clock


def test_clock_init():
    """Test basic initialization of the Clock class."""
    clock = Clock()
    assert clock.parent is None
    assert not clock.paused
    assert clock.skew == 0.0
    assert clock.paused_at is None


def test_clock_with_parent():
    """Test initialization with a parent clock."""
    parent = Clock()
    child = Clock(parent=parent)
    assert child.parent == parent


def test_clock_time_property():
    """Test the time property returns current time with skew."""
    # Using patch to control time.time() output
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        clock = Clock()
        assert clock.time == 100.0  # Default time with no skew

        # Test with skew
        clock.skew = 10.0
        assert clock.time == 110.0


def test_clock_parent_time_property():
    """Test the parent_time property."""
    # Create parent with fixed time
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        parent = Clock()
        child = Clock(parent=parent)

        # Parent time should match mocked time
        assert parent.parent_time == 100.0

        # Child's parent_time should match parent's time
        assert child.parent_time == 100.0


def test_clock_time_setter():
    """Test setting the time adjusts the skew appropriately."""
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        clock = Clock()
        assert clock.time == 100.0

        # Set to a future time
        clock.time = 150.0
        assert clock.skew == 50.0
        assert clock.time == 150.0

        # Set to a past time
        clock.time = 50.0
        assert clock.skew == -50.0
        assert clock.time == 50.0


def test_parent_child_relationship():
    """Test time flows from parent to child with appropriate skews."""
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        parent = Clock()
        child = Clock(parent=parent)

        assert parent.time == 100.0
        assert child.time == 100.0

        # Adjust parent's skew
        parent.skew = 20.0
        assert parent.time == 120.0
        assert child.time == 120.0

        # Adjust child's skew
        child.skew = 10.0
        assert parent.time == 120.0
        assert child.time == 130.0


def test_clock_pause():
    """Test pausing a clock freezes its time."""
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        clock = Clock()
        clock.pause()

        assert clock.paused
        assert clock.paused_at == 100.0

        # Time should remain frozen
        mock_time.return_value = 150.0
        assert clock.time == 100.0


def test_clock_resume():
    """Test resuming a clock with the correct skew adjustment."""
    with patch("ansi_stdio.clock.time") as mock_time:
        # Start at t=100
        mock_time.return_value = 100.0

        clock = Clock()
        clock.pause()

        # Time advances to t=150 while paused
        mock_time.return_value = 150.0

        # Resume should adjust skew to maintain continuity
        clock.resume()

        assert not clock.paused
        assert clock.paused_at is None

        # Skew should be -50 to keep time at 100 (where it was paused)
        assert clock.skew == -50.0
        assert clock.time == 100.0

        # Time should now advance normally from the resumed point
        mock_time.return_value = 170.0
        assert clock.time == 120.0  # 170 + (-50)


def test_nested_pause_resume():
    """Test pausing and resuming with nested clocks."""
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        parent = Clock()
        child = Clock(parent=parent)

        # Pause the parent
        parent.pause()

        # Time advances
        mock_time.return_value = 150.0

        # Both clocks should be frozen
        assert parent.time == 100.0
        assert child.time == 100.0

        # Resume the parent
        parent.resume()

        # Parent should have skew to keep it at 100
        assert parent.skew == -50.0

        # Both should now advance from 100
        mock_time.return_value = 170.0
        assert parent.time == 120.0  # 170 + (-50)
        assert child.time == 120.0


def test_multiple_pause_resume_cycles():
    """Test multiple pause/resume cycles maintain correct time."""
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        clock = Clock()

        # First pause/resume cycle
        clock.pause()
        mock_time.return_value = 120.0
        clock.resume()  # Should add skew of -20

        assert clock.skew == -20.0
        assert clock.time == 100.0

        # Let some time pass
        mock_time.return_value = 130.0
        assert clock.time == 110.0  # 130 + (-20)

        # Second pause/resume cycle
        clock.pause()
        mock_time.return_value = 150.0
        clock.resume()  # Should adjust skew by (110 - 150) = -40

        # Total skew should be -20 + (-40) = -60 now
        assert clock.skew == -60.0
        assert clock.time == 90.0  # 150 + (-60)

        # Time continues from there
        mock_time.return_value = 180.0
        assert clock.time == 120.0  # 180 + (-60)


def test_real_time_behavior():
    """Test with real time to validate actual behavior (not mocked)."""
    # This test uses actual sleep, so we use small values
    clock = Clock()

    # Record initial time
    initial_time = clock.time

    # Sleep briefly
    sleep(0.01)

    # Time should advance
    assert clock.time > initial_time

    # Now pause
    clock.pause()
    paused_time = clock.time

    # Sleep again
    sleep(0.01)

    # Time should remain frozen
    assert clock.time == paused_time

    # Resume
    clock.resume()
    resumed_time = clock.time

    # Time should be close to the paused time (accounting for minimal processing delays)
    assert abs(resumed_time - paused_time) < 0.005

    # Sleep one more time
    sleep(0.01)

    # Time should advance again from where we resumed
    assert clock.time > resumed_time


def test_set_time_while_paused():
    """Test setting time while a clock is paused."""
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        clock = Clock()
        clock.pause()

        # Time should be frozen at 100.0
        assert clock.time == 100.0

        # Set time while paused
        clock.time = 200.0

        # Time should be updated to the new value while remaining paused
        assert clock.time == 200.0
        assert clock.paused
        assert clock.paused_at == 200.0

        # Advance system time
        mock_time.return_value = 150.0

        # Clock should still be at 200.0 since it's paused
        assert clock.time == 200.0

        # Resume and check skew
        clock.resume()
        assert not clock.paused
        assert clock.skew == 200.0 - 150.0  # skew should preserve the paused time
        assert clock.time == 200.0


def test_child_with_paused_parent():
    """Test behavior of child clock when parent is paused."""
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        parent = Clock()
        child = Clock(parent=parent)

        # Both should be at system time initially
        assert parent.time == 100.0
        assert child.time == 100.0

        # Pause parent
        parent.pause()

        # Advance system time
        mock_time.return_value = 150.0

        # Parent should be frozen
        assert parent.time == 100.0

        # Child should also be frozen since its time comes from parent
        assert child.time == 100.0

        # Child is not itself paused though
        assert not child.paused


def test_change_parent():
    """Test changing a clock's parent."""
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        parent1 = Clock()
        parent2 = Clock()
        child = Clock(parent=parent1)

        # Initial state
        assert child.parent == parent1
        assert child.time == 100.0

        # Set skew on parent1
        parent1.skew = 50.0
        assert parent1.time == 150.0
        assert child.time == 150.0

        # Change parent
        child.parent = parent2
        assert child.parent == parent2

        # Child now follows parent2
        assert child.time == 100.0

        # Add skew to maintain original time
        child.skew = 50.0
        assert child.time == 150.0


def test_set_time_on_child_clock():
    """Test setting time on a child clock."""
    with patch("ansi_stdio.clock.time") as mock_time:
        mock_time.return_value = 100.0

        parent = Clock()
        child = Clock(parent=parent)

        # Initial state
        assert parent.time == 100.0
        assert child.time == 100.0

        # Set parent skew
        parent.skew = 20.0
        assert parent.time == 120.0
        assert child.time == 120.0

        # Set child time
        child.time = 150.0

        # Child skew should be adjusted relative to parent
        assert child.skew == 30.0  # 150 - 120
        assert child.time == 150.0

        # Parent remains unchanged
        assert parent.time == 120.0

        # Advancing system time
        mock_time.return_value = 110.0

        # Parent advances
        assert parent.time == 130.0  # 110 + 20

        # Child follows with its own skew
        assert child.time == 160.0  # 130 + 30

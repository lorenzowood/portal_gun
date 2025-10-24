"""Mock time module for testing MicroPython code locally."""


class MockTime:
    """Controllable time for deterministic testing"""

    def __init__(self):
        self._current_ms = 0
        self._sleep_total = 0

    def ticks_ms(self):
        """Return current time in milliseconds"""
        return self._current_ms

    def ticks_diff(self, new, old):
        """Calculate difference between ticks, handling overflow"""
        # MicroPython ticks can overflow at ~12 days
        # For testing, we'll keep it simple
        diff = new - old
        # Handle wraparound (simplified for 32-bit)
        if diff > 0x3FFFFFFF:
            diff -= 0x80000000
        elif diff < -0x3FFFFFFF:
            diff += 0x80000000
        return diff

    def ticks_add(self, ticks, delta):
        """Add delta to ticks, handling overflow"""
        return (ticks + delta) & 0x7FFFFFFF

    def sleep_ms(self, ms):
        """Sleep for specified milliseconds"""
        self._current_ms += ms
        self._sleep_total += ms

    def sleep(self, seconds):
        """Sleep for specified seconds"""
        self.sleep_ms(int(seconds * 1000))

    def advance(self, ms):
        """Test helper: advance time without sleeping"""
        self._current_ms += ms

    def reset(self):
        """Test helper: reset time to zero"""
        self._current_ms = 0
        self._sleep_total = 0

    def set(self, ms):
        """Test helper: set absolute time"""
        self._current_ms = ms


# Global instance for easy access
_mock_time = MockTime()

# Export functions that match standard time module
ticks_ms = _mock_time.ticks_ms
ticks_diff = _mock_time.ticks_diff
ticks_add = _mock_time.ticks_add
sleep_ms = _mock_time.sleep_ms
sleep = _mock_time.sleep

# Test helpers
advance = _mock_time.advance
reset = _mock_time.reset
set_time = _mock_time.set
get_instance = lambda: _mock_time

"""Mock neopixel module for testing MicroPython code locally."""


class NeoPixel:
    """Mock NeoPixel class simulating MicroPython neopixel.NeoPixel"""

    def __init__(self, pin, n, bpp=3):
        """
        Initialize NeoPixel strip

        Args:
            pin: Pin object (mocked)
            n: Number of pixels
            bpp: Bytes per pixel (3 for RGB, 4 for RGBW)
        """
        self.pin = pin
        self.n = n
        self.bpp = bpp
        self._data = [(0, 0, 0)] * n  # Store as RGB tuples

    def __len__(self):
        """Return number of pixels"""
        return self.n

    def __getitem__(self, index):
        """Get pixel color at index"""
        return self._data[index]

    def __setitem__(self, index, val):
        """Set pixel color at index"""
        if isinstance(val, (tuple, list)):
            if len(val) == 3:
                self._data[index] = tuple(val)
            else:
                raise ValueError("Color must be RGB tuple")
        else:
            raise ValueError("Color must be tuple or list")

    def write(self):
        """Write data to strip (no-op in mock)"""
        pass

    def fill(self, color):
        """Fill all pixels with color"""
        for i in range(self.n):
            self[i] = color
        self.write()

    def get_state(self):
        """Test helper to get current state of all pixels"""
        return list(self._data)

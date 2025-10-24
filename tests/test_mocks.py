"""Tests for mock modules."""

import pytest
from tests.mocks import mock_machine, mock_neopixel, mock_time


class TestMockPin:
    """Test mock Pin class"""

    def test_pin_creation(self):
        """Test creating a pin"""
        pin = mock_machine.Pin(16, mock_machine.Pin.OUT)
        assert pin.pin_id == 16
        assert pin.mode == mock_machine.Pin.OUT

    def test_pin_value(self):
        """Test setting and getting pin value"""
        pin = mock_machine.Pin(16, mock_machine.Pin.OUT)
        pin.value(1)
        assert pin.value() == 1
        pin.value(0)
        assert pin.value() == 0

    def test_pin_on_off(self):
        """Test pin on/off methods"""
        pin = mock_machine.Pin(16, mock_machine.Pin.OUT)
        pin.on()
        assert pin.value() == 1
        pin.off()
        assert pin.value() == 0

    def test_pin_irq(self):
        """Test pin interrupt handling"""
        pin = mock_machine.Pin(12, mock_machine.Pin.IN, mock_machine.Pin.PULL_UP)
        called = []

        def handler(p):
            called.append(p)

        pin.irq(handler=handler, trigger=mock_machine.Pin.IRQ_FALLING)
        pin._trigger_irq()
        assert len(called) == 1
        assert called[0] == pin


class TestMockPWM:
    """Test mock PWM class"""

    def test_pwm_creation(self):
        """Test creating PWM on a pin"""
        pin = mock_machine.Pin(13, mock_machine.Pin.OUT)
        pwm = mock_machine.PWM(pin)
        assert pwm.pin == pin
        assert pwm.freq() == 1000

    def test_pwm_frequency(self):
        """Test setting PWM frequency"""
        pin = mock_machine.Pin(13, mock_machine.Pin.OUT)
        pwm = mock_machine.PWM(pin)
        pwm.freq(2000)
        assert pwm.freq() == 2000

    def test_pwm_duty_cycle(self):
        """Test setting PWM duty cycle"""
        pin = mock_machine.Pin(13, mock_machine.Pin.OUT)
        pwm = mock_machine.PWM(pin)
        pwm.duty_u16(32768)
        assert pwm.duty_u16() == 32768

    def test_pwm_duty_cycle_clamping(self):
        """Test PWM duty cycle is clamped to valid range"""
        pin = mock_machine.Pin(13, mock_machine.Pin.OUT)
        pwm = mock_machine.PWM(pin)
        pwm.duty_u16(70000)  # Too high
        assert pwm.duty_u16() == 65535
        pwm.duty_u16(-100)  # Too low
        assert pwm.duty_u16() == 0


class TestMockNeoPixel:
    """Test mock NeoPixel class"""

    def test_neopixel_creation(self):
        """Test creating NeoPixel strip"""
        pin = mock_machine.Pin(16, mock_machine.Pin.OUT)
        np = mock_neopixel.NeoPixel(pin, 15)
        assert len(np) == 15
        assert np.n == 15
        assert np.bpp == 3

    def test_neopixel_set_get(self):
        """Test setting and getting pixel colors"""
        pin = mock_machine.Pin(16, mock_machine.Pin.OUT)
        np = mock_neopixel.NeoPixel(pin, 15)
        np[0] = (255, 128, 64)
        assert np[0] == (255, 128, 64)

    def test_neopixel_fill(self):
        """Test filling all pixels"""
        pin = mock_machine.Pin(16, mock_machine.Pin.OUT)
        np = mock_neopixel.NeoPixel(pin, 15)
        np.fill((100, 50, 25))
        for i in range(15):
            assert np[i] == (100, 50, 25)

    def test_neopixel_initial_state(self):
        """Test pixels start at (0, 0, 0)"""
        pin = mock_machine.Pin(16, mock_machine.Pin.OUT)
        np = mock_neopixel.NeoPixel(pin, 15)
        for i in range(15):
            assert np[i] == (0, 0, 0)


class TestMockTime:
    """Test mock time module"""

    def test_ticks_ms(self):
        """Test ticks_ms returns current time"""
        assert mock_time.ticks_ms() == 0
        mock_time.advance(100)
        assert mock_time.ticks_ms() == 100

    def test_ticks_diff(self):
        """Test ticks_diff calculates difference"""
        t1 = mock_time.ticks_ms()
        mock_time.advance(500)
        t2 = mock_time.ticks_ms()
        assert mock_time.ticks_diff(t2, t1) == 500

    def test_ticks_add(self):
        """Test ticks_add adds delta"""
        t = 1000
        t2 = mock_time.ticks_add(t, 500)
        assert t2 == 1500

    def test_sleep_ms(self):
        """Test sleep_ms advances time"""
        t1 = mock_time.ticks_ms()
        mock_time.sleep_ms(250)
        t2 = mock_time.ticks_ms()
        assert mock_time.ticks_diff(t2, t1) == 250

    def test_reset(self):
        """Test reset returns time to zero"""
        mock_time.advance(5000)
        assert mock_time.ticks_ms() == 5000
        mock_time.reset()
        assert mock_time.ticks_ms() == 0

    def test_set_time(self):
        """Test set_time sets absolute time"""
        mock_time.set_time(12345)
        assert mock_time.ticks_ms() == 12345

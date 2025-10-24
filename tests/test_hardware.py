"""Tests for hardware abstraction layer."""

import pytest
from tests.mocks import mock_machine, mock_neopixel
from config import Config


# Import will fail initially - that's expected for TDD
try:
    from hardware import (
        LEDController,
        DisplayController,
        NeopixelController,
        EncoderReader,
        ButtonReader,
        HardwareManager,
        HardwareError
    )
except ImportError:
    pass


class TestLEDController:
    """Test LED controller"""

    def test_led_creation(self):
        """Test creating LED controller"""
        leds = LEDController(
            pins=[Config.PIN_LED_1, Config.PIN_LED_2, Config.PIN_LED_3],
            active_low=True
        )
        assert leds is not None
        assert leds.num_leds == 3

    def test_led_set_brightness(self):
        """Test setting LED brightness"""
        leds = LEDController(
            pins=[Config.PIN_LED_1, Config.PIN_LED_2, Config.PIN_LED_3],
            active_low=True
        )
        leds.set_brightness(0, 100)  # LED 0 to 100%
        leds.set_brightness(1, 50)   # LED 1 to 50%
        leds.set_brightness(2, 0)    # LED 2 to 0%

    def test_led_set_all_brightness(self):
        """Test setting all LEDs to same brightness"""
        leds = LEDController(
            pins=[Config.PIN_LED_1, Config.PIN_LED_2, Config.PIN_LED_3],
            active_low=True
        )
        leds.set_all_brightness(75)
        # Can't easily verify PWM values in mock, but should not crash

    def test_led_off(self):
        """Test turning all LEDs off"""
        leds = LEDController(
            pins=[Config.PIN_LED_1, Config.PIN_LED_2, Config.PIN_LED_3],
            active_low=True
        )
        leds.off()
        # Should not crash


class TestDisplayController:
    """Test display controller"""

    def test_display_creation(self):
        """Test creating display controller"""
        display = DisplayController(Config.PIN_DISPLAY_CLK, Config.PIN_DISPLAY_DIO)
        assert display is not None

    def test_display_show_text(self):
        """Test showing text"""
        display = DisplayController(Config.PIN_DISPLAY_CLK, Config.PIN_DISPLAY_DIO)
        display.show_text("C137")
        display.show_text("Stby")
        display.show_text("    ")  # Blank

    def test_display_show_number(self):
        """Test showing number"""
        display = DisplayController(Config.PIN_DISPLAY_CLK, Config.PIN_DISPLAY_DIO)
        display.show_number(1337)
        display.show_number(0)
        display.show_number(9999)

    def test_display_clear(self):
        """Test clearing display"""
        display = DisplayController(Config.PIN_DISPLAY_CLK, Config.PIN_DISPLAY_DIO)
        display.clear()

    def test_display_brightness(self):
        """Test setting display brightness"""
        display = DisplayController(Config.PIN_DISPLAY_CLK, Config.PIN_DISPLAY_DIO)
        display.set_brightness(7)  # Max brightness
        display.set_brightness(0)  # Min brightness


class TestNeopixelController:
    """Test neopixel controller"""

    def test_neopixel_creation(self):
        """Test creating neopixel controller"""
        pixels = NeopixelController(Config.PIN_NEOPIXEL, Config.NUM_PIXELS)
        assert pixels is not None
        assert pixels.num_pixels == Config.NUM_PIXELS

    def test_neopixel_set_pixel(self):
        """Test setting individual pixel"""
        pixels = NeopixelController(Config.PIN_NEOPIXEL, Config.NUM_PIXELS)
        pixels.set_pixel(0, (100, 0, 0))  # Red at 100%
        pixels.set_pixel(7, (0, 100, 0))  # Green at 100%

    def test_neopixel_set_all(self):
        """Test setting all pixels"""
        pixels = NeopixelController(Config.PIN_NEOPIXEL, Config.NUM_PIXELS)
        pixels.set_all((50, 50, 50))

    def test_neopixel_off(self):
        """Test turning all pixels off"""
        pixels = NeopixelController(Config.PIN_NEOPIXEL, Config.NUM_PIXELS)
        pixels.off()

    def test_neopixel_write(self):
        """Test writing to strip"""
        pixels = NeopixelController(Config.PIN_NEOPIXEL, Config.NUM_PIXELS)
        pixels.set_pixel(0, (100, 0, 0))
        pixels.write()  # Commit changes

    def test_neopixel_get_pixel(self):
        """Test getting pixel value"""
        pixels = NeopixelController(Config.PIN_NEOPIXEL, Config.NUM_PIXELS)
        pixels.set_pixel(5, (25, 50, 75))
        color = pixels.get_pixel(5)
        assert color == (63, 127, 191)  # Converted to 0-255


class TestEncoderReader:
    """Test encoder reader"""

    def test_encoder_creation(self):
        """Test creating encoder reader"""
        encoder = EncoderReader(Config.PIN_ENCODER_CLK, Config.PIN_ENCODER_DT)
        assert encoder is not None

    def test_encoder_read(self):
        """Test reading encoder"""
        encoder = EncoderReader(Config.PIN_ENCODER_CLK, Config.PIN_ENCODER_DT)
        delta = encoder.read()
        assert isinstance(delta, int)


class TestButtonReader:
    """Test button reader"""

    def test_button_creation(self):
        """Test creating button reader"""
        button = ButtonReader(Config.PIN_ENCODER_SW)
        assert button is not None

    def test_button_is_pressed(self):
        """Test checking if button is pressed"""
        button = ButtonReader(Config.PIN_ENCODER_SW)
        pressed = button.is_pressed()
        assert isinstance(pressed, bool)

    def test_button_set_handler(self):
        """Test setting interrupt handler"""
        button = ButtonReader(Config.PIN_ENCODER_SW)
        called = []

        def handler():
            called.append(True)

        button.set_handler(handler)
        # Can't easily trigger in test, but should not crash


class TestHardwareManager:
    """Test hardware manager"""

    def test_hardware_manager_init_success(self):
        """Test successful hardware initialization"""
        hw = HardwareManager()
        assert hw.leds is not None
        assert hw.display is not None
        assert hw.pixels is not None
        assert hw.encoder is not None
        assert hw.button is not None
        assert len(hw.errors) == 0

    def test_hardware_manager_shutdown(self):
        """Test hardware shutdown"""
        hw = HardwareManager()
        hw.shutdown()
        # Should not crash

    def test_hardware_manager_has_errors(self):
        """Test checking for errors"""
        hw = HardwareManager()
        assert hw.has_errors() == (len(hw.errors) > 0)

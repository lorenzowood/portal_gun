"""Tests for configuration module."""

import pytest
from config import Config


class TestConfig:
    """Test configuration values and helpers"""

    def test_pin_assignments_exist(self):
        """Test all pin assignments are defined"""
        assert hasattr(Config, 'PIN_LED_1')
        assert hasattr(Config, 'PIN_LED_2')
        assert hasattr(Config, 'PIN_LED_3')
        assert hasattr(Config, 'PIN_NEOPIXEL')
        assert hasattr(Config, 'PIN_DISPLAY_DIO')
        assert hasattr(Config, 'PIN_DISPLAY_CLK')
        assert hasattr(Config, 'PIN_ENCODER_CLK')
        assert hasattr(Config, 'PIN_ENCODER_DT')
        assert hasattr(Config, 'PIN_ENCODER_SW')

    def test_hardware_parameters(self):
        """Test hardware parameters are defined and reasonable"""
        assert Config.NUM_PIXELS > 0
        assert Config.NUM_PIXELS == 15  # Current hardware
        assert isinstance(Config.LEDS_ACTIVE_LOW, bool)

    def test_timing_parameters(self):
        """Test timing parameters are defined and reasonable"""
        assert Config.LONG_PRESS_MS > 0
        assert Config.IDLE_TIMEOUT_MS > 0
        assert Config.STANDBY_DISPLAY_TIME_MS > 0
        assert Config.EDIT_FLASH_RATE_MS > 0
        assert 0 < Config.EDIT_FLASH_DUTY < 1

    def test_color_definitions(self):
        """Test color definitions are valid RGB tuples"""
        colors = [
            Config.COLOR_GREEN,
            Config.COLOR_BLUE_WHITE,
            Config.COLOR_PORTAL_BACKGROUND,
        ]
        for color in colors:
            assert len(color) == 3
            assert all(0 <= c <= 100 for c in color)

    def test_background_animation_params(self):
        """Test background animation parameters"""
        # Gentle motion
        assert 0 <= Config.GENTLE_MOTION_MAX_BRIGHTNESS <= 100
        assert Config.GENTLE_MOTION_RAMP_UP_MS > 0
        assert Config.GENTLE_MOTION_HOLD_MS >= 0
        assert Config.GENTLE_MOTION_RAMP_DOWN_MS > 0
        assert Config.GENTLE_MOTION_DECAY_PIXELS >= 0
        assert 0 < Config.GENTLE_MOTION_DECAY_RATE <= 1
        assert Config.GENTLE_MOTION_INTERVAL_MS > 0

        # Sparkle
        assert 0 <= Config.SPARKLE_MAX_BRIGHTNESS <= 100
        assert Config.SPARKLE_RAMP_UP_MS >= 0
        assert Config.SPARKLE_HOLD_MS >= 0
        assert Config.SPARKLE_RAMP_DOWN_MS >= 0
        assert Config.SPARKLE_GROUP_MIN <= Config.SPARKLE_GROUP_MAX

    def test_portal_generation_params(self):
        """Test portal generation parameters"""
        # Prepare
        assert Config.PORTAL_PREPARE_DURATION_MS > 0
        assert Config.PORTAL_PREPARE_FLASHES > 0

        # Ramp up
        assert Config.PORTAL_RAMPUP_DURATION_MS > 0
        assert 0 <= Config.PORTAL_RAMPUP_CENTER_BRIGHTNESS <= 100

        # Generate
        assert Config.PORTAL_GENERATE_DURATION_MS > 0
        assert 0 <= Config.PORTAL_GENERATE_THROB_MAX <= 100
        assert 0 <= Config.PORTAL_GENERATE_THROB_MIN <= 100

        # Ramp down
        assert Config.PORTAL_RAMPDOWN_DURATION_MS > 0

    def test_get_center_pixel(self):
        """Test getting center pixel index"""
        center = Config.get_center_pixel()
        assert isinstance(center, int)
        assert 0 <= center < Config.NUM_PIXELS
        # For 15 pixels, center should be 7 (0-indexed)
        assert center == 7

    def test_color_to_rgb(self):
        """Test converting percentage color to RGB bytes"""
        # Pure green at 100%
        rgb = Config.color_to_rgb((0, 100, 0))
        assert rgb == (0, 255, 0)

        # 50% brightness
        rgb = Config.color_to_rgb((50, 50, 50))
        assert rgb == (127, 127, 127)

        # Blue-white
        rgb = Config.color_to_rgb(Config.COLOR_BLUE_WHITE)
        assert len(rgb) == 3
        assert all(isinstance(c, int) for c in rgb)
        assert all(0 <= c <= 255 for c in rgb)

    def test_brightness_to_duty(self):
        """Test converting brightness to PWM duty cycle"""
        # 0% brightness
        duty = Config.brightness_to_duty(0)
        assert duty == 0

        # 100% brightness
        duty = Config.brightness_to_duty(100)
        assert duty == 65535

        # 50% brightness
        duty = Config.brightness_to_duty(50)
        assert duty == 32767  # Approximately half

    def test_brightness_to_duty_active_low(self):
        """Test brightness to duty with active-LOW logic"""
        # 0% brightness (active-LOW = fully HIGH)
        duty = Config.brightness_to_duty(0, active_low=True)
        assert duty == 65535

        # 100% brightness (active-LOW = fully LOW)
        duty = Config.brightness_to_duty(100, active_low=True)
        assert duty == 0

        # 50% brightness (active-LOW = inverted)
        duty = Config.brightness_to_duty(50, active_low=True)
        assert duty == 32768  # Approximately half (inverted)

    def test_universe_code_default(self):
        """Test default universe code"""
        assert Config.UNIVERSE_CODE_DEFAULT == "C137"

    def test_config_is_modifiable(self):
        """Test that config values can be modified (for testing/tuning)"""
        original = Config.NUM_PIXELS
        Config.NUM_PIXELS = 20
        assert Config.NUM_PIXELS == 20
        # Restore
        Config.NUM_PIXELS = original

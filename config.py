"""Portal Gun configuration - all tunable parameters."""


class Config:
    """Centralized configuration for Portal Gun prop"""

    # ========== HARDWARE ==========

    # Pin assignments
    PIN_LED_1 = 13  # Active-LOW
    PIN_LED_2 = 14  # Active-LOW
    PIN_LED_3 = 15  # Active-LOW
    PIN_NEOPIXEL = 16
    PIN_DISPLAY_DIO = 6
    PIN_DISPLAY_CLK = 7
    PIN_ENCODER_CLK = 10
    PIN_ENCODER_DT = 11
    PIN_ENCODER_SW = 12

    # Hardware parameters
    NUM_PIXELS = 15  # Number of neopixels in strip
    LEDS_ACTIVE_LOW = True  # LEDs turn on when pin is LOW

    # ========== TIMING ==========

    # Input timing
    LONG_PRESS_MS = 700  # Threshold for long press detection
    IDLE_TIMEOUT_MS = 3 * 60 * 1000  # 3 minutes until standby

    # Standby mode
    STANDBY_DISPLAY_TIME_MS = 3000  # Show "Stby" for 3 seconds

    # Universe code edit mode
    EDIT_FLASH_RATE_MS = 300  # Flash period for editing character
    EDIT_FLASH_DUTY = 0.5  # 50% duty cycle

    # Error display
    ERROR_FLASH_HZ = 3  # Flash rate for error codes
    ERROR_PAUSE_MS = 1000  # Pause between error code sequences

    # ========== COLORS ==========

    # Colors as (R, G, B) tuples with brightness 0-100%
    COLOR_GREEN = (0, 100, 0)
    COLOR_BLUE_WHITE = (94, 94, 100)  # 240,240,255 scaled to percentage
    COLOR_PORTAL_BACKGROUND = (0, 75, 0)  # 0,192,0 scaled

    # ========== BACKGROUND ANIMATIONS ==========

    # Gentle motion effect
    GENTLE_MOTION_MAX_BRIGHTNESS = 50  # Percent
    GENTLE_MOTION_COLOR = COLOR_GREEN
    GENTLE_MOTION_RAMP_UP_MS = 3000
    GENTLE_MOTION_HOLD_MS = 1000
    GENTLE_MOTION_RAMP_DOWN_MS = 3000
    GENTLE_MOTION_DECAY_PIXELS = 2  # Pixels either side affected
    GENTLE_MOTION_DECAY_RATE = 0.5  # 50% brightness decrease per pixel
    GENTLE_MOTION_INTERVAL_MS = 5000  # Time between starting new effects

    # Sparkle effect
    SPARKLE_MAX_BRIGHTNESS = 100  # Percent
    SPARKLE_COLOR = COLOR_BLUE_WHITE
    SPARKLE_RAMP_UP_MS = 20
    SPARKLE_HOLD_MS = 0
    SPARKLE_RAMP_DOWN_MS = 500
    SPARKLE_GROUP_MIN = 1  # Min sparkles per group
    SPARKLE_GROUP_MAX = 5  # Max sparkles per group
    SPARKLE_WITHIN_GROUP_MIN_MS = 200  # Min time between sparkles in group
    SPARKLE_WITHIN_GROUP_MAX_MS = 500  # Max time between sparkles in group
    SPARKLE_BETWEEN_GROUPS_MIN_MS = 2000  # Min time between groups
    SPARKLE_BETWEEN_GROUPS_MAX_MS = 5000  # Max time between groups

    # ========== PORTAL GENERATION ==========

    # Phase 1: Preparing to fire
    PORTAL_PREPARE_DURATION_MS = 500
    PORTAL_PREPARE_FLASHES = 3
    PORTAL_PREPARE_FLASH_OFF_MS = 50
    PORTAL_PREPARE_FLASH_ON_MS = 100

    # Phase 2: Ramping up
    PORTAL_RAMPUP_DURATION_MS = 1000
    PORTAL_RAMPUP_CENTER_BRIGHTNESS = 100  # Percent
    PORTAL_RAMPUP_CENTER_COLOR = COLOR_GREEN
    PORTAL_RAMPUP_FLASH_MIN = 50  # Flash between 50% and 100%
    PORTAL_RAMPUP_FLASH_MAX = 100
    PORTAL_RAMPUP_FLASH_LOW_MS = 10
    PORTAL_RAMPUP_FLASH_HIGH_MS = 20
    PORTAL_RAMPUP_PIXEL_DELAY_MS = 100  # Delay per pixel from center
    PORTAL_RAMPUP_DISPLAY_UPDATE_MS = 100  # Cycle display every 100ms

    # Phase 3: Generating
    PORTAL_GENERATE_DURATION_MS = 3000
    PORTAL_GENERATE_BG_COLOR = COLOR_PORTAL_BACKGROUND
    PORTAL_GENERATE_FG_COLOR = COLOR_BLUE_WHITE
    PORTAL_GENERATE_THROB_INITIAL_MS = 100  # Ramp to 90% in 100ms
    PORTAL_GENERATE_THROB_MAX = 90  # Max throb extension (percent)
    PORTAL_GENERATE_THROB_MIN = 40  # Min throb extension (percent)
    PORTAL_GENERATE_THROB_DOWN_MS = 80  # 90% to 40% in 80ms
    PORTAL_GENERATE_THROB_UP_MS = 40  # 40% to 90% in 40ms
    PORTAL_GENERATE_LED_BRIGHTNESS = 100  # Percent
    PORTAL_GENERATE_LED_RAMP_MS = 100
    PORTAL_GENERATE_LED_OSC_MAX = 100  # Oscillate between 100% and 50%
    PORTAL_GENERATE_LED_OSC_MIN = 50
    PORTAL_GENERATE_LED_NOISE = 20  # ±20% noise
    PORTAL_GENERATE_LED_NOISE_HZ = 20

    # Phase 4: Ramping down
    PORTAL_RAMPDOWN_DURATION_MS = 2000
    PORTAL_RAMPDOWN_DISPLAY_ON_MS = 250
    PORTAL_RAMPDOWN_DISPLAY_OFF_MS = 50

    # ========== UNIVERSE CODE ==========

    UNIVERSE_CODE_DEFAULT = "C137"  # Initial universe code

    # ========== HELPERS ==========

    @staticmethod
    def get_center_pixel():
        """Get the center pixel index"""
        return Config.NUM_PIXELS // 2

    @staticmethod
    def color_to_rgb(color_percent):
        """Convert color percentage (0-100) to RGB byte values (0-255)"""
        return tuple(int(c * 255 / 100) for c in color_percent)

    @staticmethod
    def brightness_to_duty(brightness_percent, active_low=False):
        """Convert brightness percentage to PWM duty cycle (0-65535)"""
        duty = int(brightness_percent * 65535 / 100)
        if active_low:
            duty = 65535 - duty
        return duty

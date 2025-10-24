"""Hardware abstraction layer for Portal Gun.

Provides mockable interfaces to all hardware components.
"""

from machine import Pin, PWM
import neopixel
from config import Config

# Try to import tm1637, but allow tests to work without it
try:
    from tm1637 import TM1637
except ImportError:
    TM1637 = None


class HardwareError(Exception):
    """Hardware initialization or operation error"""
    pass


class LEDController:
    """Control three front LEDs with PWM brightness control"""

    def __init__(self, pins, active_low=True):
        """
        Initialize LED controller

        Args:
            pins: List of pin numbers for LEDs
            active_low: If True, LEDs turn on when pin is LOW
        """
        self.pins = pins
        self.active_low = active_low
        self.num_leds = len(pins)

        # Initialize PWM for each LED
        self.pwms = []
        for pin_num in pins:
            pin = Pin(pin_num, Pin.OUT)
            pwm = PWM(pin)
            pwm.freq(1000)  # 1kHz PWM
            self.pwms.append(pwm)

        self.off()

    def set_brightness(self, index, brightness):
        """
        Set brightness of a single LED

        Args:
            index: LED index (0-2)
            brightness: Brightness 0-100 percent
        """
        if not (0 <= index < self.num_leds):
            return
        duty = Config.brightness_to_duty(brightness, self.active_low)
        self.pwms[index].duty_u16(duty)

    def set_all_brightness(self, brightness):
        """
        Set all LEDs to same brightness

        Args:
            brightness: Brightness 0-100 percent
        """
        for i in range(self.num_leds):
            self.set_brightness(i, brightness)

    def off(self):
        """Turn all LEDs off"""
        self.set_all_brightness(0)

    def shutdown(self):
        """Clean up resources"""
        self.off()
        for pwm in self.pwms:
            pwm.deinit()


class DisplayController:
    """Control TM1637 7-segment display"""

    def __init__(self, clk_pin, dio_pin):
        """
        Initialize display controller

        Args:
            clk_pin: Clock pin number
            dio_pin: Data pin number

        Raises:
            HardwareError: If display init fails
        """
        if TM1637 is None:
            # Running in test mode without real TM1637
            self.display = None
            self._mock_brightness = 7
            return

        try:
            self.display = TM1637(Pin(clk_pin), Pin(dio_pin))
            self.display.brightness = 7
            self.clear()
        except Exception as e:
            raise HardwareError(f"Display init failed: {e}")

    def show_text(self, text):
        """
        Show text on display

        Args:
            text: String up to 4 characters
        """
        if self.display:
            self.display.text(text[:4].upper())
        # In mock mode, just accept the call

    def show_number(self, number):
        """
        Show number on display

        Args:
            number: Number 0-9999
        """
        if self.display:
            self.display.number(number)
        # In mock mode, just accept the call

    def clear(self):
        """Clear display"""
        self.show_text("    ")

    def set_brightness(self, level):
        """
        Set display brightness

        Args:
            level: Brightness 0-7
        """
        if self.display:
            self.display.brightness = max(0, min(7, level))
        else:
            self._mock_brightness = level

    def shutdown(self):
        """Clean up resources"""
        self.clear()


class NeopixelController:
    """Control WS2814 RGB neopixel strip"""

    def __init__(self, pin, num_pixels):
        """
        Initialize neopixel controller

        Args:
            pin: Data pin number
            num_pixels: Number of pixels in strip

        Raises:
            HardwareError: If neopixel init fails
        """
        self.num_pixels = num_pixels

        try:
            self.pixels = neopixel.NeoPixel(Pin(pin, Pin.OUT), num_pixels)
            self.off()
        except Exception as e:
            raise HardwareError(f"Neopixel init failed: {e}")

    def set_pixel(self, index, color):
        """
        Set individual pixel color

        Args:
            index: Pixel index (0 to num_pixels-1)
            color: RGB tuple with values 0-100 (percent)
        """
        if not (0 <= index < self.num_pixels):
            return
        # Convert percentage (0-100) to byte values (0-255)
        rgb = Config.color_to_rgb(color)
        self.pixels[index] = rgb

    def get_pixel(self, index):
        """
        Get current pixel color

        Args:
            index: Pixel index

        Returns:
            RGB tuple (0-255)
        """
        if not (0 <= index < self.num_pixels):
            return (0, 0, 0)
        return self.pixels[index]

    def set_all(self, color):
        """
        Set all pixels to same color

        Args:
            color: RGB tuple with values 0-100 (percent)
        """
        rgb = Config.color_to_rgb(color)
        self.pixels.fill(rgb)

    def off(self):
        """Turn all pixels off"""
        self.pixels.fill((0, 0, 0))
        self.write()

    def write(self):
        """Commit pixel changes to strip"""
        self.pixels.write()

    def shutdown(self):
        """Clean up resources"""
        self.off()


class EncoderReader:
    """Read rotary encoder rotation using interrupts like encoder_test.py"""

    def __init__(self, clk_pin, dt_pin):
        """
        Initialize encoder reader with interrupt handling

        Args:
            clk_pin: Clock pin number
            dt_pin: Data pin number
        """
        self.clk_pin = Pin(clk_pin, Pin.IN, Pin.PULL_UP)
        self.dt_pin = Pin(dt_pin, Pin.IN, Pin.PULL_UP)
        self.last_clk_state = self.clk_pin.value()
        self.position = 0

        # Event queue - buffered encoder changes
        self.events = []

        # Set up interrupt on CLK pin (both edges)
        self.clk_pin.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=self._encoder_changed)

    def _encoder_changed(self, pin):
        """
        Interrupt handler - called when CLK pin changes

        This is the same logic as encoder_test.py
        """
        clk_state = self.clk_pin.value()
        dt_state = self.dt_pin.value()

        # If CLK changed from HIGH to LOW (falling edge)
        if self.last_clk_state == 1 and clk_state == 0:
            if dt_state == 0:
                # Clockwise
                self.events.append(1)
                self.position += 1
            else:
                # Counter-clockwise
                self.events.append(-1)
                self.position -= 1

        self.last_clk_state = clk_state

    def read(self):
        """
        Read buffered encoder events

        Returns:
            Delta: +1 for clockwise, -1 for counter-clockwise, 0 for no change
        """
        if self.events:
            return self.events.pop(0)
        return 0


class ButtonReader:
    """Read button state with interrupt support"""

    def __init__(self, pin):
        """
        Initialize button reader

        Args:
            pin: Button pin number
        """
        self.pin = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.handler = None

    def is_pressed(self):
        """
        Check if button is currently pressed

        Returns:
            True if pressed (LOW), False otherwise
        """
        return self.pin.value() == 0

    def set_handler(self, handler):
        """
        Set interrupt handler for button press

        Args:
            handler: Callback function (no arguments)
        """
        self.handler = handler
        if handler:
            # Trigger on falling edge (button press)
            self.pin.irq(trigger=Pin.IRQ_FALLING, handler=lambda p: handler())


class HardwareManager:
    """Manage all hardware components with error handling"""

    # Error codes for LED flash patterns
    ERROR_DISPLAY = 1
    ERROR_NEOPIXELS = 2

    def __init__(self):
        """
        Initialize all hardware components

        Errors are collected but don't stop initialization
        """
        self.errors = []
        self.leds = None
        self.display = None
        self.pixels = None
        self.encoder = None
        self.button = None

        # Initialize LEDs first (least likely to fail, used for error display)
        try:
            self.leds = LEDController(
                pins=[Config.PIN_LED_1, Config.PIN_LED_2, Config.PIN_LED_3],
                active_low=Config.LEDS_ACTIVE_LOW
            )
        except Exception as e:
            # If LEDs fail, we can't show errors, so just continue
            self.errors.append((None, str(e)))

        # Initialize display
        try:
            self.display = DisplayController(
                Config.PIN_DISPLAY_CLK,
                Config.PIN_DISPLAY_DIO
            )
        except HardwareError as e:
            self.errors.append((self.ERROR_DISPLAY, str(e)))

        # Initialize neopixels
        try:
            self.pixels = NeopixelController(
                Config.PIN_NEOPIXEL,
                Config.NUM_PIXELS
            )
        except HardwareError as e:
            self.errors.append((self.ERROR_NEOPIXELS, str(e)))

        # Initialize encoder (no error code, less critical)
        try:
            self.encoder = EncoderReader(
                Config.PIN_ENCODER_CLK,
                Config.PIN_ENCODER_DT
            )
        except Exception as e:
            self.errors.append((None, str(e)))

        # Initialize button (no error code, less critical)
        try:
            self.button = ButtonReader(Config.PIN_ENCODER_SW)
        except Exception as e:
            self.errors.append((None, str(e)))

    def has_errors(self):
        """
        Check if any hardware errors occurred

        Returns:
            True if errors present
        """
        return len(self.errors) > 0

    def get_error_codes(self):
        """
        Get list of error codes for display

        Returns:
            List of error code numbers (ignores None codes)
        """
        return [code for code, msg in self.errors if code is not None]

    def shutdown(self):
        """Cleanly shut down all hardware"""
        if self.leds:
            self.leds.shutdown()
        if self.display:
            self.display.shutdown()
        if self.pixels:
            self.pixels.shutdown()

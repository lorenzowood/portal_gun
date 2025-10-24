"""Input handler for Portal Gun.

Handles encoder, button, long press detection, and idle timeout.
"""

import time
from config import Config
from hardware import HardwareManager


class InputEvent:
    """Input event types"""

    ENCODER_CW = 'encoder_cw'
    ENCODER_CCW = 'encoder_ccw'
    BUTTON_SHORT = 'button_short'
    BUTTON_LONG = 'button_long'
    IDLE_TIMEOUT = 'idle_timeout'

    def __init__(self, event_type):
        """
        Create input event

        Args:
            event_type: Event type constant
        """
        self.type = event_type

    def __repr__(self):
        return f"InputEvent({self.type})"


class InputHandler:
    """Handles all user input with event generation"""

    def __init__(self, hardware=None):
        """
        Initialize input handler

        Args:
            hardware: HardwareManager instance (or None to create one)
        """
        self.hardware = hardware or HardwareManager()

        # Button state
        self.button_pressed = False
        self.button_press_time = None
        self.long_press_fired = False

        # Encoder state
        self.last_encoder_position = 0

        # Idle timeout
        self.last_activity_time = time.ticks_ms()
        self.idle_timeout_fired = False

        # Event queue for internal methods
        self._event_queue = []

    def _on_button_press(self):
        """Handle button press (internal)"""
        self.button_pressed = True
        self.button_press_time = time.ticks_ms()
        self.long_press_fired = False
        self.reset_idle_timer()

    def _on_button_release(self):
        """Handle button release (internal)"""
        self.button_pressed = False
        # Queue short press event if long press didn't fire
        if not self.long_press_fired:
            self._event_queue.append(InputEvent(InputEvent.BUTTON_SHORT))
            self.reset_idle_timer()

    def reset_idle_timer(self):
        """Reset the idle timeout timer"""
        self.last_activity_time = time.ticks_ms()
        self.idle_timeout_fired = False

    def poll(self):
        """
        Poll for input events

        Returns:
            List of InputEvent objects
        """
        # Start with queued events
        events = list(self._event_queue)
        self._event_queue.clear()

        now = time.ticks_ms()

        # Check encoder
        if self.hardware.encoder:
            current_position = self.hardware.encoder.position
            delta = current_position - self.last_encoder_position

            if delta != 0:
                self.reset_idle_timer()
                # Generate events for each click
                if delta > 0:
                    for _ in range(delta):
                        events.append(InputEvent(InputEvent.ENCODER_CW))
                else:
                    for _ in range(abs(delta)):
                        events.append(InputEvent(InputEvent.ENCODER_CCW))

                self.last_encoder_position = current_position

        # Check button state
        if self.hardware.button:
            button_is_pressed = self.hardware.button.is_pressed()

            # Detect button press
            if button_is_pressed and not self.button_pressed:
                self._on_button_press()

            # Detect button release
            if not button_is_pressed and self.button_pressed:
                self._on_button_release()
                # Short press event is queued in _on_button_release()

            # Check for long press
            if self.button_pressed and not self.long_press_fired:
                if self.button_press_time is not None:
                    press_duration = time.ticks_diff(now, self.button_press_time)
                    if press_duration >= Config.LONG_PRESS_MS:
                        events.append(InputEvent(InputEvent.BUTTON_LONG))
                        self.long_press_fired = True
                        self.reset_idle_timer()

        # Check idle timeout
        if not self.idle_timeout_fired:
            idle_time = time.ticks_diff(now, self.last_activity_time)
            if idle_time >= Config.IDLE_TIMEOUT_MS:
                events.append(InputEvent(InputEvent.IDLE_TIMEOUT))
                self.idle_timeout_fired = True

        return events

    def setup_interrupts(self):
        """
        Set up interrupt handlers (for use on real hardware)

        Note: In test mode with mocks, this won't do anything useful
        """
        if self.hardware.button:
            # On real hardware, button interrupts would call _on_button_press
            # For now, we poll in poll() method instead
            pass

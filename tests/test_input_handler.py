"""Tests for input handler."""

import pytest
from tests.mocks import mock_time
from config import Config


# Import will fail initially - that's expected for TDD
try:
    from input_handler import InputHandler, InputEvent
except ImportError:
    pass


class TestInputHandler:
    """Test input handler"""

    def test_input_handler_creation(self):
        """Test creating input handler"""
        handler = InputHandler()
        assert handler is not None

    def test_encoder_clockwise(self):
        """Test detecting encoder clockwise rotation"""
        mock_time.reset()
        handler = InputHandler()

        # Simulate encoder returning +1
        handler.hardware.encoder.position += 1

        events = handler.poll()
        assert len(events) == 1
        assert events[0].type == InputEvent.ENCODER_CW

    def test_encoder_counterclockwise(self):
        """Test detecting encoder counterclockwise rotation"""
        mock_time.reset()
        handler = InputHandler()

        # Simulate encoder returning -1
        handler.hardware.encoder.position -= 1

        events = handler.poll()
        assert len(events) == 1
        assert events[0].type == InputEvent.ENCODER_CCW

    def test_short_button_press(self):
        """Test detecting short button press"""
        mock_time.reset()
        handler = InputHandler()

        # Simulate button press
        handler._on_button_press()

        # Wait less than long press threshold
        mock_time.advance(Config.LONG_PRESS_MS - 100)

        # Simulate button release
        handler._on_button_release()

        events = handler.poll()
        assert any(e.type == InputEvent.BUTTON_SHORT for e in events)

    def test_long_button_press(self):
        """Test detecting long button press"""
        mock_time.reset()
        handler = InputHandler()

        # Simulate button press by setting pin LOW
        handler.hardware.button.pin.value(0)

        # First poll to detect button press
        handler.poll()

        # Wait longer than long press threshold
        mock_time.advance(Config.LONG_PRESS_MS + 100)

        # Check for long press
        events = handler.poll()
        assert any(e.type == InputEvent.BUTTON_LONG for e in events)

    def test_button_long_press_only_once(self):
        """Test long press only fires once"""
        mock_time.reset()
        handler = InputHandler()

        # Simulate button press by setting pin LOW
        handler.hardware.button.pin.value(0)

        # First poll to detect button press
        handler.poll()

        # Wait for long press
        mock_time.advance(Config.LONG_PRESS_MS + 100)
        events = handler.poll()
        assert any(e.type == InputEvent.BUTTON_LONG for e in events)

        # Poll again - should not get another long press
        mock_time.advance(100)
        events = handler.poll()
        assert not any(e.type == InputEvent.BUTTON_LONG for e in events)

    def test_idle_timeout(self):
        """Test idle timeout detection"""
        mock_time.reset()
        handler = InputHandler()

        # Poll normally - no timeout
        events = handler.poll()
        assert not any(e.type == InputEvent.IDLE_TIMEOUT for e in events)

        # Advance past idle timeout
        mock_time.advance(Config.IDLE_TIMEOUT_MS + 1000)

        # Should get timeout event
        events = handler.poll()
        assert any(e.type == InputEvent.IDLE_TIMEOUT for e in events)

    def test_idle_reset_on_input(self):
        """Test idle timer resets on input"""
        mock_time.reset()
        handler = InputHandler()

        # Advance partway to timeout
        mock_time.advance(Config.IDLE_TIMEOUT_MS - 1000)

        # Generate input (encoder)
        handler.hardware.encoder.position += 1
        events = handler.poll()

        # Advance again (but less than full timeout from input)
        mock_time.advance(Config.IDLE_TIMEOUT_MS - 1000)

        # Should not timeout yet
        events = handler.poll()
        assert not any(e.type == InputEvent.IDLE_TIMEOUT for e in events)

    def test_reset_idle_timer(self):
        """Test manually resetting idle timer"""
        mock_time.reset()
        handler = InputHandler()

        # Advance partway to timeout
        mock_time.advance(Config.IDLE_TIMEOUT_MS - 1000)

        # Manually reset
        handler.reset_idle_timer()

        # Advance again
        mock_time.advance(Config.IDLE_TIMEOUT_MS - 1000)

        # Should not timeout
        events = handler.poll()
        assert not any(e.type == InputEvent.IDLE_TIMEOUT for e in events)

    def test_multiple_encoder_changes(self):
        """Test multiple encoder changes in one poll"""
        mock_time.reset()
        handler = InputHandler()

        # Simulate multiple clicks
        handler.hardware.encoder.position += 3

        events = handler.poll()
        # Should get 3 clockwise events
        cw_events = [e for e in events if e.type == InputEvent.ENCODER_CW]
        assert len(cw_events) == 3


class TestInputEvent:
    """Test input event class"""

    def test_input_event_creation(self):
        """Test creating input event"""
        event = InputEvent(InputEvent.ENCODER_CW)
        assert event.type == InputEvent.ENCODER_CW

    def test_input_event_types_exist(self):
        """Test all event types are defined"""
        assert hasattr(InputEvent, 'ENCODER_CW')
        assert hasattr(InputEvent, 'ENCODER_CCW')
        assert hasattr(InputEvent, 'BUTTON_SHORT')
        assert hasattr(InputEvent, 'BUTTON_LONG')
        assert hasattr(InputEvent, 'IDLE_TIMEOUT')

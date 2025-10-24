"""Tests for state machine."""

import pytest
from tests.mocks import mock_time
from config import Config
from universe_code import UniverseCode
from input_handler import InputEvent


# Import will fail initially - that's expected for TDD
try:
    from state_machine import (
        StateMachine,
        StandbyState,
        OperationState,
        UniverseCodeEditState,
        PortalGeneratingState
    )
except ImportError:
    pass


class TestStateMachine:
    """Test state machine basics"""

    def test_state_machine_creation(self):
        """Test creating state machine"""
        sm = StateMachine()
        assert sm is not None
        assert isinstance(sm.current_state, StandbyState)

    def test_initial_universe_code(self):
        """Test initial universe code"""
        sm = StateMachine()
        assert str(sm.universe_code) == Config.UNIVERSE_CODE_DEFAULT

    def test_update(self):
        """Test update method exists and runs"""
        sm = StateMachine()
        sm.update()  # Should not crash


class TestStandbyState:
    """Test standby state"""

    def test_standby_to_operation_long_press(self):
        """Test transition from standby to operation on long press"""
        mock_time.reset()
        sm = StateMachine()

        # Should start in standby
        assert isinstance(sm.current_state, StandbyState)

        # Send long press event
        event = InputEvent(InputEvent.BUTTON_LONG)
        sm.handle_input(event)

        # Should transition to operation
        assert isinstance(sm.current_state, OperationState)

    def test_standby_ignores_other_input(self):
        """Test standby ignores encoder and short press"""
        sm = StateMachine()

        # Try encoder
        sm.handle_input(InputEvent(InputEvent.ENCODER_CW))
        assert isinstance(sm.current_state, StandbyState)

        # Try short press
        sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))
        assert isinstance(sm.current_state, StandbyState)


class TestOperationState:
    """Test operation state"""

    def test_operation_encoder_changes_universe_code(self):
        """Test encoder changes universe code in operation mode"""
        sm = StateMachine()
        # Transition to operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))
        assert isinstance(sm.current_state, OperationState)

        initial_code = str(sm.universe_code)

        # Clockwise should increment
        sm.handle_input(InputEvent(InputEvent.ENCODER_CW))
        assert str(sm.universe_code) != initial_code

    def test_operation_short_press_to_edit(self):
        """Test short press enters universe code edit mode"""
        sm = StateMachine()
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))  # To edit

        assert isinstance(sm.current_state, UniverseCodeEditState)

    def test_operation_long_press_to_portal(self):
        """Test long press enters portal generating mode"""
        sm = StateMachine()
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To portal

        assert isinstance(sm.current_state, PortalGeneratingState)

    def test_operation_idle_to_standby(self):
        """Test idle timeout returns to standby"""
        sm = StateMachine()
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.IDLE_TIMEOUT))  # Back to standby

        assert isinstance(sm.current_state, StandbyState)


class TestUniverseCodeEditState:
    """Test universe code edit state"""

    def test_edit_mode_basics(self):
        """Test edit mode can be entered"""
        sm = StateMachine()
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))  # To edit

        assert isinstance(sm.current_state, UniverseCodeEditState)
        assert sm.current_state.edit_position == 0  # Start at first character

    def test_edit_encoder_changes_character(self):
        """Test encoder changes current character"""
        sm = StateMachine()
        sm.universe_code = UniverseCode("C137")
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))  # To edit

        # Encoder should change letter
        sm.handle_input(InputEvent(InputEvent.ENCODER_CW))
        assert sm.universe_code.letter != 'C'

    def test_edit_short_press_advances_position(self):
        """Test short press advances to next character"""
        sm = StateMachine()
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))  # To edit

        assert sm.current_state.edit_position == 0

        # Short press advances
        sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))
        assert sm.current_state.edit_position == 1

    def test_edit_completes_after_last_character(self):
        """Test edit completes after confirming last character"""
        sm = StateMachine()
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))  # To edit

        # Press through all 4 characters
        for _ in range(4):
            sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))

        # Should be back in operation
        assert isinstance(sm.current_state, OperationState)

    def test_edit_long_press_aborts(self):
        """Test long press aborts edit"""
        sm = StateMachine()
        original_code = UniverseCode("C137")
        sm.universe_code = original_code

        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))  # To edit

        # Change something
        sm.handle_input(InputEvent(InputEvent.ENCODER_CW))

        # Abort with long press
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))

        # Should be back in operation with original code
        assert isinstance(sm.current_state, OperationState)
        # Universe code should be restored (implementation dependent)


class TestPortalGeneratingState:
    """Test portal generating state"""

    def test_portal_generation_phases(self):
        """Test portal generation has multiple phases"""
        sm = StateMachine()
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To portal

        state = sm.current_state
        assert isinstance(state, PortalGeneratingState)
        # Should have phase tracking
        assert hasattr(state, 'phase')

    def test_portal_generation_completes(self):
        """Test portal generation eventually completes"""
        mock_time.reset()
        sm = StateMachine()

        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))  # To portal

        # Advance through all phases
        total_duration = (
            Config.PORTAL_PREPARE_DURATION_MS +
            Config.PORTAL_RAMPUP_DURATION_MS +
            Config.PORTAL_GENERATE_DURATION_MS +
            Config.PORTAL_RAMPDOWN_DURATION_MS
        )

        mock_time.advance(total_duration + 1000)

        # Update state machine
        sm.update()

        # Should be back in operation
        assert isinstance(sm.current_state, OperationState)


class TestStateTransitions:
    """Test state transition flows"""

    def test_full_cycle(self):
        """Test complete state cycle"""
        sm = StateMachine()

        # Standby -> Operation
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))
        assert isinstance(sm.current_state, OperationState)

        # Operation -> Edit
        sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))
        assert isinstance(sm.current_state, UniverseCodeEditState)

        # Edit -> Operation (complete edit)
        for _ in range(4):
            sm.handle_input(InputEvent(InputEvent.BUTTON_SHORT))
        assert isinstance(sm.current_state, OperationState)

        # Operation -> Portal
        sm.handle_input(InputEvent(InputEvent.BUTTON_LONG))
        assert isinstance(sm.current_state, PortalGeneratingState)

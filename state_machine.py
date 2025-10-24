"""State machine for Portal Gun modes.

Manages state transitions and mode behaviors.
"""

import time
from config import Config
from universe_code import UniverseCode
from input_handler import InputEvent


class State:
    """Base state class"""

    def __init__(self, machine):
        """
        Initialize state

        Args:
            machine: StateMachine instance
        """
        self.machine = machine

    def enter(self):
        """Called when entering this state"""
        pass

    def exit(self):
        """Called when exiting this state"""
        pass

    def handle_input(self, event):
        """
        Handle input event

        Args:
            event: InputEvent instance

        Returns:
            New state or None to stay in current state
        """
        return None

    def update(self):
        """
        Update state (called every frame)

        Returns:
            New state or None to stay in current state
        """
        return None


class StandbyState(State):
    """Standby mode - low power, waiting for activation"""

    def enter(self):
        """Enter standby mode"""
        self.entry_time = time.ticks_ms()

    def handle_input(self, event):
        """Handle input in standby mode"""
        if event.type == InputEvent.BUTTON_LONG:
            return OperationState(self.machine)
        return None


class OperationState(State):
    """Operation mode - normal operation, can adjust universe code"""

    def enter(self):
        """Enter operation mode"""
        pass

    def handle_input(self, event):
        """Handle input in operation mode"""
        if event.type == InputEvent.BUTTON_SHORT:
            return UniverseCodeEditState(self.machine)
        elif event.type == InputEvent.BUTTON_LONG:
            return PortalGeneratingState(self.machine)
        elif event.type == InputEvent.IDLE_TIMEOUT:
            return StandbyState(self.machine)
        elif event.type == InputEvent.ENCODER_CW:
            self.machine.universe_code.increment()
        elif event.type == InputEvent.ENCODER_CCW:
            self.machine.universe_code.decrement()
        return None


class UniverseCodeEditState(State):
    """Universe code edit mode - edit individual characters"""

    def __init__(self, machine):
        super().__init__(machine)
        self.edit_position = 0  # 0=letter, 1-3=digits
        self.original_code = str(machine.universe_code)
        self.enter_time = None

    def enter(self):
        """Enter edit mode"""
        self.edit_position = 0
        self.enter_time = time.ticks_ms()

    def handle_input(self, event):
        """Handle input in edit mode"""
        if event.type == InputEvent.BUTTON_LONG:
            # Abort edit, restore original
            self.machine.universe_code = UniverseCode(self.original_code)
            return OperationState(self.machine)

        elif event.type == InputEvent.BUTTON_SHORT:
            # Advance to next position
            self.edit_position += 1
            if self.edit_position >= 4:
                # Completed editing all characters
                return OperationState(self.machine)

        elif event.type == InputEvent.ENCODER_CW:
            self._increment_current_character()

        elif event.type == InputEvent.ENCODER_CCW:
            self._decrement_current_character()

        return None

    def _increment_current_character(self):
        """Increment the character at current edit position"""
        if self.edit_position == 0:
            # Editing letter
            self.machine.universe_code.increment_letter()
        else:
            # Editing digit (position 1-3 maps to digit 0-2)
            digit_pos = self.edit_position - 1
            self.machine.universe_code.increment_digit(digit_pos)

    def _decrement_current_character(self):
        """Decrement the character at current edit position"""
        if self.edit_position == 0:
            # Editing letter
            self.machine.universe_code.decrement_letter()
        else:
            # Editing digit
            digit_pos = self.edit_position - 1
            self.machine.universe_code.decrement_digit(digit_pos)


class PortalGeneratingState(State):
    """Portal generating mode - animated sequence"""

    # Phase constants
    PHASE_PREPARE = 0
    PHASE_RAMPUP = 1
    PHASE_GENERATE = 2
    PHASE_RAMPDOWN = 3
    PHASE_COMPLETE = 4

    def __init__(self, machine):
        super().__init__(machine)
        self.phase = self.PHASE_PREPARE
        self.start_time = None
        self.phase_start_time = None

    def enter(self):
        """Enter portal generation mode"""
        self.phase = self.PHASE_PREPARE
        self.start_time = time.ticks_ms()
        self.phase_start_time = self.start_time
        print(f"Portal generation started - PHASE_PREPARE")

    def update(self):
        """Update portal generation"""
        if self.start_time is None or self.phase_start_time is None:
            return None

        now = time.ticks_ms()

        # Debug: show we're updating
        if now % 1000 < 20:
            print(f"Portal update: phase={self.phase}, elapsed_total={time.ticks_diff(now, self.start_time)}ms")

        # Process all completed phases (in case update() is called after long delay)
        while self.phase < self.PHASE_COMPLETE:
            phase_elapsed = time.ticks_diff(now, self.phase_start_time)
            phase_complete = False

            if self.phase == self.PHASE_PREPARE:
                if phase_elapsed >= Config.PORTAL_PREPARE_DURATION_MS:
                    phase_complete = True
            elif self.phase == self.PHASE_RAMPUP:
                if phase_elapsed >= Config.PORTAL_RAMPUP_DURATION_MS:
                    phase_complete = True
            elif self.phase == self.PHASE_GENERATE:
                if phase_elapsed >= Config.PORTAL_GENERATE_DURATION_MS:
                    phase_complete = True
            elif self.phase == self.PHASE_RAMPDOWN:
                if phase_elapsed >= Config.PORTAL_RAMPDOWN_DURATION_MS:
                    phase_complete = True

            if phase_complete:
                old_phase = self.phase
                self.phase += 1
                print(f">>> Phase complete! {old_phase} -> {self.phase}, phase_elapsed={phase_elapsed}ms")
                # Advance phase start time by phase duration
                if self.phase == self.PHASE_RAMPUP:
                    self.phase_start_time = time.ticks_add(
                        self.phase_start_time, Config.PORTAL_PREPARE_DURATION_MS)
                    print(f"Portal phase: PREPARE -> RAMPUP (elapsed={phase_elapsed}ms)")
                elif self.phase == self.PHASE_GENERATE:
                    self.phase_start_time = time.ticks_add(
                        self.phase_start_time, Config.PORTAL_RAMPUP_DURATION_MS)
                    print(f"Portal phase: RAMPUP -> GENERATE (elapsed={phase_elapsed}ms)")
                elif self.phase == self.PHASE_RAMPDOWN:
                    self.phase_start_time = time.ticks_add(
                        self.phase_start_time, Config.PORTAL_GENERATE_DURATION_MS)
                    print(f"Portal phase: GENERATE -> RAMPDOWN (elapsed={phase_elapsed}ms)")
                elif self.phase == self.PHASE_COMPLETE:
                    # All phases complete, return to operation
                    print(f"Portal phase: RAMPDOWN -> COMPLETE (elapsed={phase_elapsed}ms)")
                    print("Portal generation complete, returning to operation mode")
                    return OperationState(self.machine)
            else:
                # Current phase not complete yet
                break

        # If we get here, all phases are complete or current phase not done
        if self.phase >= self.PHASE_COMPLETE:
            print(f"!!! Portal should be complete but didn't return! phase={self.phase}")
        return None


class StateMachine:
    """Main state machine coordinator"""

    def __init__(self):
        """Initialize state machine"""
        self.universe_code = UniverseCode(Config.UNIVERSE_CODE_DEFAULT)
        self.current_state = StandbyState(self)
        self.current_state.enter()

    def handle_input(self, event):
        """
        Handle input event

        Args:
            event: InputEvent instance
        """
        new_state = self.current_state.handle_input(event)
        if new_state is not None:
            self._transition_to(new_state)

    def update(self):
        """Update state machine (call every frame)"""
        new_state = self.current_state.update()
        if new_state is not None:
            self._transition_to(new_state)

    def _transition_to(self, new_state):
        """
        Transition to a new state

        Args:
            new_state: State instance
        """
        self.current_state.exit()
        self.current_state = new_state
        self.current_state.enter()

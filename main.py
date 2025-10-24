"""Portal Gun main controller.

Coordinates all subsystems: hardware, state machine, animations, input.
"""

import time
from config import Config
from hardware import HardwareManager
from state_machine import StateMachine, StandbyState, OperationState, UniverseCodeEditState, PortalGeneratingState
from input_handler import InputHandler
from animations import AnimationCompositor, GentleMotionManager, SparkleGroupManager


class PortalGun:
    """Main Portal Gun controller"""

    def __init__(self):
        """Initialize all subsystems"""
        print("Portal Gun initializing...")

        # Initialize hardware
        self.hardware = HardwareManager()

        # Check for hardware errors
        if self.hardware.has_errors():
            print(f"Hardware errors: {self.hardware.get_error_codes()}")
            # Error display will be handled in main loop
        else:
            print("Hardware initialized successfully")

        # Initialize state machine
        self.state_machine = StateMachine()
        print(f"Initial universe code: {self.state_machine.universe_code}")

        # Initialize input handler (reuses hardware manager)
        self.input_handler = InputHandler(hardware=self.hardware)

        # Initialize animation system
        self.compositor = AnimationCompositor(num_pixels=Config.NUM_PIXELS)
        self.gentle_motion_manager = GentleMotionManager(self.compositor, Config)
        self.sparkle_manager = SparkleGroupManager(self.compositor, Config)

        # Background animations enabled flag
        self.background_animations_enabled = False

        # Error display state
        self.error_display_active = False
        self.error_flash_state = False
        self.error_last_flash_time = 0
        self.error_index = 0

        print("Portal Gun ready!")

    def run(self):
        """Main loop"""
        print("Starting main loop...")

        while True:
            try:
                # Get current time
                now = time.ticks_ms()

                # Handle hardware errors
                if self.hardware.has_errors():
                    self._update_error_display(now)
                    time.sleep_ms(10)
                    continue

                # Poll for input events
                events = self.input_handler.poll()

                # Handle each event
                for event in events:
                    print(f"Event: {event.type}, State: {type(self.state_machine.current_state).__name__}, Code: {self.state_machine.universe_code}")
                    self.state_machine.handle_input(event)
                    # Reset idle timer on any input (except idle timeout itself)
                    if event.type != 'idle_timeout':
                        self.input_handler.reset_idle_timer()

                # Update state machine
                self.state_machine.update()

                # Update display based on current state
                self._update_display()

                # Update animations based on current state
                self._update_animations()

                # Update LEDs based on current state
                self._update_leds()

                # Small delay to prevent CPU spinning (3ms for smoother animations)
                time.sleep_ms(3)

                idle_elapsed = time.ticks_diff(now, self.input_handler.last_activity_time)
                if idle_elapsed % 10000 < 20:  # Print every ~10 seconds
                    print(f"Idle: {idle_elapsed}ms")      

            except KeyboardInterrupt:
                print("\\nShutdown requested")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                import sys
                sys.print_exception(e)
                time.sleep_ms(1000)

        # Cleanup
        self._shutdown()

    def _update_error_display(self, now):
        """Display error codes via center LED"""
        error_codes = self.hardware.get_error_codes()
        if not error_codes:
            return

        # Flash pattern: 3Hz (150ms on, 183ms off), 1s pause between codes
        if self.error_flash_state:
            # LED is on, check if time to turn off
            if time.ticks_diff(now, self.error_last_flash_time) >= 150:
                if self.hardware.leds:
                    self.hardware.leds.set_brightness(1, 0)  # Center LED off
                self.error_flash_state = False
                self.error_last_flash_time = now
        else:
            # LED is off, check if time for next flash or pause
            elapsed = time.ticks_diff(now, self.error_last_flash_time)

            # Get current error code and how many flashes we've shown
            current_error_index = self.error_index % len(error_codes)
            current_code = error_codes[current_error_index]

            # Calculate which flash we're on (1-indexed)
            flash_cycle_time = 333  # 150ms on + 183ms off
            flash_num = (elapsed // flash_cycle_time) + 1

            if flash_num <= current_code:
                # Time for next flash
                if elapsed >= (flash_num - 1) * flash_cycle_time + 183:
                    if self.hardware.leds:
                        self.hardware.leds.set_brightness(1, 100)  # Center LED on
                    self.error_flash_state = True
                    self.error_last_flash_time = now
            else:
                # Finished flashing this code, wait for pause
                if elapsed >= current_code * flash_cycle_time + 1000:
                    # Move to next error code
                    self.error_index += 1
                    self.error_last_flash_time = now

    def _update_display(self):
        """Update display based on current state"""
        if not self.hardware.display:
            return

        state = self.state_machine.current_state

        if isinstance(state, StandbyState):
            # Show "Stby" briefly, then turn off
            elapsed = time.ticks_diff(time.ticks_ms(), state.entry_time)
            if elapsed < Config.STANDBY_DISPLAY_TIME_MS:
                self.hardware.display.show_text("Stby")
            else:
                self.hardware.display.clear()

        elif isinstance(state, OperationState):
            # Show current universe code
            self.hardware.display.show_text(str(self.state_machine.universe_code))

        elif isinstance(state, UniverseCodeEditState):
            # Show universe code with flashing character being edited
            code_str = str(self.state_machine.universe_code)
            edit_pos = state.edit_position

            # Build display string: confirmed chars + current char (maybe flashing) + spaces
            display_str = ""
            for i in range(4):
                if i < edit_pos:
                    # Already confirmed - show it
                    display_str += code_str[i]
                elif i == edit_pos:
                    # Currently editing - flash it
                    if state.enter_time is not None:
                        elapsed = time.ticks_diff(time.ticks_ms(), state.enter_time)
                        flash_period = Config.EDIT_FLASH_RATE_MS
                        flash_on = (elapsed % flash_period) < (flash_period * Config.EDIT_FLASH_DUTY)
                    else:
                        flash_on = True

                    if flash_on:
                        display_str += code_str[i]
                    else:
                        display_str += " "
                else:
                    # Not confirmed yet - blank
                    display_str += " "

            self.hardware.display.show_text(display_str)

        elif isinstance(state, PortalGeneratingState):
            # Phase-specific display animations
            now = time.ticks_ms()
            phase_elapsed = time.ticks_diff(now, state.phase_start_time) if state.phase_start_time else 0
            final_code = str(self.state_machine.universe_code)

            if state.phase == state.PHASE_PREPARE:
                # Flash universe code 3 times (50ms off, 100ms on), then solid
                flash_cycle = 150  # 50ms off + 100ms on
                flash_num = phase_elapsed // flash_cycle
                if flash_num >= Config.PORTAL_PREPARE_FLASHES:
                    # After 3 flashes, show solid
                    self.hardware.display.show_text(final_code)
                else:
                    # Within flash cycle
                    in_cycle = phase_elapsed % flash_cycle
                    if in_cycle < Config.PORTAL_PREPARE_FLASH_OFF_MS:
                        # Off period
                        self.hardware.display.clear()
                    else:
                        # On period
                        self.hardware.display.show_text(final_code)

            elif state.phase == state.PHASE_RAMPUP:
                # Random letters and digits every 100ms
                import random
                cycle_count = phase_elapsed // Config.PORTAL_RAMPUP_DISPLAY_UPDATE_MS
                random.seed(cycle_count)  # Deterministic based on time
                # First char: random letter A-F
                letter = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
                # Other chars: random digits
                d1 = random.randint(0, 9)
                d2 = random.randint(0, 9)
                d3 = random.randint(0, 9)
                display_str = f"{letter}{d1}{d2}{d3}"
                self.hardware.display.show_text(display_str)

            elif state.phase == state.PHASE_GENERATE:
                # Progressive lock-in of characters
                # Divide phase into 4 equal parts (one per character)
                lock_interval = Config.PORTAL_GENERATE_DURATION_MS / 4
                num_locked = int(phase_elapsed / lock_interval)
                if num_locked > 4:
                    num_locked = 4

                # Build display string
                import random
                cycle_count = phase_elapsed // Config.PORTAL_DISPLAY_CYCLE_MS
                random.seed(cycle_count)
                display_str = ""
                for i in range(4):
                    if i < num_locked:
                        # Locked - show actual character
                        display_str += final_code[i]
                    else:
                        # Unlocked - random cycling
                        if i == 0:
                            letter = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
                            display_str += letter
                        else:
                            digit = str(random.randint(0, 9))
                            display_str += digit

                self.hardware.display.show_text(display_str)

            elif state.phase == state.PHASE_RAMPDOWN:
                # Flash final code (250ms on, 50ms off)
                flash_cycle = Config.PORTAL_RAMPDOWN_DISPLAY_ON_MS + Config.PORTAL_RAMPDOWN_DISPLAY_OFF_MS
                in_cycle = phase_elapsed % flash_cycle
                if in_cycle < Config.PORTAL_RAMPDOWN_DISPLAY_ON_MS:
                    # On period
                    self.hardware.display.show_text(final_code)
                else:
                    # Off period
                    self.hardware.display.clear()

            else:
                # COMPLETE or unknown - show code
                self.hardware.display.show_text(final_code)

    def _update_animations(self):
        """Update neopixel animations based on current state"""
        if not self.hardware.pixels:
            return

        state = self.state_machine.current_state

        # Enable/disable background animations based on state
        if isinstance(state, (OperationState, UniverseCodeEditState)):
            if not self.background_animations_enabled:
                self.background_animations_enabled = True
                # Start first animations
                self.gentle_motion_manager.next_motion_time = time.ticks_ms()
                self.sparkle_manager.next_sparkle_time = time.ticks_ms()

            # Update background animations
            self.gentle_motion_manager.update()
            self.sparkle_manager.update()

        elif isinstance(state, StandbyState):
            if self.background_animations_enabled:
                self.background_animations_enabled = False
                self.compositor.clear_animations()

        elif isinstance(state, PortalGeneratingState):
            # Portal animation (simplified - basic effect for now)
            # TODO: Implement full portal animation phases (throb, etc.)
            if self.background_animations_enabled:
                self.background_animations_enabled = False
                self.compositor.clear_animations()
                print("Portal animations: cleared background animations")

            # Portal throb effect during generate phase
            if state.phase == state.PHASE_GENERATE:
                now = time.ticks_ms()
                phase_elapsed = time.ticks_diff(now, state.phase_start_time) if state.phase_start_time else 0

                # Get throb extension (0-100%)
                throb_extension = self._get_throb_extension(phase_elapsed)

                center_pixel = Config.get_center_pixel()
                max_distance = center_pixel  # Distance from center to edge

                # Calculate throb reach (how far from center the foreground spreads)
                throb_reach = (throb_extension / 100.0) * max_distance

                for i in range(Config.NUM_PIXELS):
                    # Calculate distance from center
                    distance = abs(i - center_pixel)

                    # Calculate foreground/background mix
                    if throb_reach == 0:
                        # No throb - only center pixel has foreground
                        foreground_mix = 1.0 if distance == 0 else 0.0
                    else:
                        # Linear falloff from center to throb_reach
                        foreground_mix = max(0.0, min(1.0, 1.0 - (distance / throb_reach)))

                    # Mix background and foreground colors
                    bg_r, bg_g, bg_b = Config.PORTAL_GENERATE_BG_COLOR
                    fg_r, fg_g, fg_b = Config.PORTAL_GENERATE_FG_COLOR

                    r = int(bg_r * (1 - foreground_mix) + fg_r * foreground_mix)
                    g = int(bg_g * (1 - foreground_mix) + fg_g * foreground_mix)
                    b = int(bg_b * (1 - foreground_mix) + fg_b * foreground_mix)

                    self.hardware.pixels.set_pixel(i, (r, g, b))
            elif state.phase == state.PHASE_RAMPUP:
                # Per-pixel delayed ramp with flashing
                now = time.ticks_ms()
                phase_elapsed = time.ticks_diff(now, state.phase_start_time) if state.phase_start_time else 0
                center_pixel = Config.get_center_pixel()

                # Flash cycle: 10ms low + 20ms high = 30ms total
                flash_cycle = Config.PORTAL_RAMPUP_FLASH_LOW_MS + Config.PORTAL_RAMPUP_FLASH_HIGH_MS
                flash_in_cycle = phase_elapsed % flash_cycle
                flash_multiplier = Config.PORTAL_RAMPUP_FLASH_MAX / 100.0  # High = 100%
                if flash_in_cycle < Config.PORTAL_RAMPUP_FLASH_LOW_MS:
                    flash_multiplier = Config.PORTAL_RAMPUP_FLASH_MIN / 100.0  # Low = 50%

                for i in range(Config.NUM_PIXELS):
                    # Calculate distance from center
                    distance = abs(i - center_pixel)

                    # Calculate when this pixel should start ramping
                    pixel_start_delay = distance * Config.PORTAL_RAMPUP_PIXEL_DELAY_MS

                    # Calculate how long this pixel has been ramping
                    pixel_ramp_time = phase_elapsed - pixel_start_delay

                    if pixel_ramp_time < 0:
                        # Pixel hasn't started yet
                        brightness = 0
                    else:
                        # Calculate ramp progress (0.0 to 1.0)
                        ramp_progress = min(1.0, pixel_ramp_time / Config.PORTAL_RAMPUP_DURATION_MS)

                        # Apply flash multiplier to current ramp level
                        brightness = int(ramp_progress * flash_multiplier * Config.PORTAL_RAMPUP_CENTER_BRIGHTNESS)

                    # Set pixel to green with calculated brightness
                    r, g, b = Config.PORTAL_RAMPUP_CENTER_COLOR
                    self.hardware.pixels.set_pixel(i, (
                        int(r * brightness / 100),
                        int(g * brightness / 100),
                        int(b * brightness / 100)
                    ))
            elif state.phase == state.PHASE_RAMPDOWN:
                # Blend fading throb with fading-in background animations
                now = time.ticks_ms()
                phase_elapsed = time.ticks_diff(now, state.phase_start_time) if state.phase_start_time else 0
                t = min(1.0, phase_elapsed / Config.PORTAL_RAMPDOWN_DURATION_MS)

                # Throb opacity: 100% -> 0% linearly over full duration
                throb_opacity = 1.0 - t

                # Background opacity: 0% -> 100%, reaching 100% at halfway point
                bg_opacity = min(1.0, t * 2.0)

                # Throb extension: drops from max to 0% linearly
                throb_extension = Config.PORTAL_GENERATE_THROB_MAX * (1.0 - t)

                # Re-enable background animations for blending
                if not self.background_animations_enabled:
                    self.background_animations_enabled = True
                    self.gentle_motion_manager.next_motion_time = time.ticks_ms()
                    self.sparkle_manager.next_sparkle_time = time.ticks_ms()

                # Update and get background animation pixels
                self.gentle_motion_manager.update()
                self.sparkle_manager.update()
                self.compositor.update()
                bg_pixels = self.compositor.get_composite()

                # Calculate throb effect
                center_pixel = Config.get_center_pixel()
                max_distance = center_pixel
                throb_reach = (throb_extension / 100.0) * max_distance

                for i in range(Config.NUM_PIXELS):
                    # Calculate throb color for this pixel
                    distance = abs(i - center_pixel)

                    if throb_reach == 0:
                        foreground_mix = 1.0 if distance == 0 else 0.0
                    else:
                        foreground_mix = max(0.0, min(1.0, 1.0 - (distance / throb_reach)))

                    bg_r, bg_g, bg_b = Config.PORTAL_GENERATE_BG_COLOR
                    fg_r, fg_g, fg_b = Config.PORTAL_GENERATE_FG_COLOR

                    throb_r = int(bg_r * (1 - foreground_mix) + fg_r * foreground_mix)
                    throb_g = int(bg_g * (1 - foreground_mix) + fg_g * foreground_mix)
                    throb_b = int(bg_b * (1 - foreground_mix) + fg_b * foreground_mix)

                    # Get background animation color
                    anim_r, anim_g, anim_b = bg_pixels[i]

                    # Blend throb and background based on their opacities
                    final_r = int(throb_r * throb_opacity + anim_r * bg_opacity)
                    final_g = int(throb_g * throb_opacity + anim_g * bg_opacity)
                    final_b = int(throb_b * throb_opacity + anim_b * bg_opacity)

                    self.hardware.pixels.set_pixel(i, (final_r, final_g, final_b))
            else:
                # PREPARE or complete - off
                for i in range(Config.NUM_PIXELS):
                    self.hardware.pixels.set_pixel(i, (0, 0, 0))

            self.hardware.pixels.write()
            return  # Don't process normal compositor

        # Update all active animations
        self.compositor.update()

        # Get composite result and write to neopixels
        pixel_colors = self.compositor.get_composite()
        for i, color in enumerate(pixel_colors):
            self.hardware.pixels.set_pixel(i, color)
        self.hardware.pixels.write()

    def _get_throb_extension(self, phase_elapsed):
        """
        Calculate throb extension percentage (0-100) based on time in GENERATE phase

        Args:
            phase_elapsed: Time elapsed in GENERATE phase (ms)

        Returns:
            Throb extension as percentage (0-100)
        """
        if phase_elapsed < Config.PORTAL_GENERATE_THROB_INITIAL_MS:
            # Initial ramp: 0% to 90% in 100ms
            t = phase_elapsed / Config.PORTAL_GENERATE_THROB_INITIAL_MS
            return t * Config.PORTAL_GENERATE_THROB_MAX
        else:
            # Oscillate between 90% and 40%
            # Cycle time: 80ms down + 40ms up = 120ms
            cycle_time = Config.PORTAL_GENERATE_THROB_DOWN_MS + Config.PORTAL_GENERATE_THROB_UP_MS
            elapsed_in_cycle = (phase_elapsed - Config.PORTAL_GENERATE_THROB_INITIAL_MS) % cycle_time

            if elapsed_in_cycle < Config.PORTAL_GENERATE_THROB_DOWN_MS:
                # Going down: 90% to 40%
                t = elapsed_in_cycle / Config.PORTAL_GENERATE_THROB_DOWN_MS
                return Config.PORTAL_GENERATE_THROB_MAX - t * (Config.PORTAL_GENERATE_THROB_MAX - Config.PORTAL_GENERATE_THROB_MIN)
            else:
                # Going up: 40% to 90%
                t = (elapsed_in_cycle - Config.PORTAL_GENERATE_THROB_DOWN_MS) / Config.PORTAL_GENERATE_THROB_UP_MS
                return Config.PORTAL_GENERATE_THROB_MIN + t * (Config.PORTAL_GENERATE_THROB_MAX - Config.PORTAL_GENERATE_THROB_MIN)

    def _update_leds(self):
        """Update front LEDs based on current state"""
        if not self.hardware.leds:
            return

        state = self.state_machine.current_state

        # LEDs are only used during portal generation
        if isinstance(state, PortalGeneratingState):
            # Phase-specific LED behavior
            now = time.ticks_ms()
            phase_elapsed = time.ticks_diff(now, state.phase_start_time) if state.phase_start_time else 0
            brightness = 0

            if state.phase == state.PHASE_PREPARE:
                # LEDs off during prepare
                brightness = 0
            elif state.phase == state.PHASE_RAMPUP:
                # Ramp up to 100% over 1 second
                t = min(1.0, phase_elapsed / Config.PORTAL_RAMPUP_DURATION_MS)
                brightness = int(t * Config.PORTAL_GENERATE_LED_BRIGHTNESS)
            elif state.phase == state.PHASE_GENERATE:
                # Oscillate with throb, plus noise
                throb = self._get_throb_extension(phase_elapsed)

                # Map throb extension (40-90%) to LED brightness (50-100%)
                # throb=40 -> brightness=50, throb=90 -> brightness=100
                throb_range = Config.PORTAL_GENERATE_THROB_MAX - Config.PORTAL_GENERATE_THROB_MIN
                led_range = Config.PORTAL_GENERATE_LED_OSC_MAX - Config.PORTAL_GENERATE_LED_OSC_MIN
                base_brightness = Config.PORTAL_GENERATE_LED_OSC_MIN + ((throb - Config.PORTAL_GENERATE_THROB_MIN) / throb_range) * led_range

                # Add noise: ±20% at 20Hz (50ms period)
                import random
                noise_cycle = int(phase_elapsed / (1000 / Config.PORTAL_GENERATE_LED_NOISE_HZ))
                random.seed(noise_cycle)
                noise = random.uniform(-Config.PORTAL_GENERATE_LED_NOISE, Config.PORTAL_GENERATE_LED_NOISE)

                brightness = int(max(0, min(100, base_brightness + noise)))
            elif state.phase == state.PHASE_RAMPDOWN:
                # Ramp down to 0% over 2 seconds
                t = min(1.0, phase_elapsed / Config.PORTAL_RAMPDOWN_DURATION_MS)
                brightness = int((1 - t) * Config.PORTAL_GENERATE_LED_BRIGHTNESS)

            self.hardware.leds.set_all_brightness(brightness)

            # Debug (occasionally)
            if now % 500 < 20:
                phase_names = ['PREPARE', 'RAMPUP', 'GENERATE', 'RAMPDOWN', 'COMPLETE']
                phase_name = phase_names[state.phase] if state.phase < len(phase_names) else 'UNKNOWN'
                print(f"Portal LEDs: phase={phase_name}, brightness={brightness}%")
        else:
            # LEDs off in other states (unless showing error codes)
            if not self.hardware.has_errors():
                self.hardware.leds.off()

    def _shutdown(self):
        """Clean shutdown"""
        print("Shutting down...")
        if self.hardware:
            self.hardware.shutdown()
        print("Shutdown complete")


# Entry point
if __name__ == "__main__":
    gun = PortalGun()
    gun.run()

# Portal Gun Implementation Plan

## Overview

This plan follows Test-Driven Development (TDD) principles:
1. Write tests first (they will fail)
2. Implement code to pass tests
3. Refactor if needed
4. Move to next step

## Architecture

The codebase will be modular and testable:

```
portal_gun/
├── config.py              # Centralized configuration
├── hardware.py            # Hardware abstraction layer (mockable)
├── universe_code.py       # Universe code logic (pure functions)
├── animations.py          # Neopixel animation engine
├── input_handler.py       # Encoder/button with long press & timeout
├── state_machine.py       # Mode management
├── main.py                # Main coordinator
├── tests/
│   ├── mocks/
│   │   ├── mock_machine.py    # Mock MicroPython machine module
│   │   ├── mock_neopixel.py   # Mock neopixel module
│   │   └── mock_time.py       # Mock time module (controllable)
│   ├── test_config.py
│   ├── test_universe_code.py
│   ├── test_animations.py
│   ├── test_input_handler.py
│   ├── test_state_machine.py
│   └── test_integration.py
└── tm1637.py              # Existing display driver
```

## Implementation Steps

### Step 0: Testing Infrastructure
**Goal**: Set up mock MicroPython environment for local testing

**Files to create**:
- `tests/mocks/mock_machine.py` - Mock Pin, PWM classes
- `tests/mocks/mock_neopixel.py` - Mock NeoPixel class
- `tests/mocks/mock_time.py` - Controllable time for testing
- `tests/test_runner.py` - Simple test runner

**Tests**: Verify mocks behave correctly
**Success criteria**: Can import mocks and run basic tests locally

---

### Step 1: Configuration Module
**Goal**: Centralized, documented configuration for all tunable parameters

**Files to create**:
- `config.py` - Configuration class with all parameters organized by category

**Tests** (`tests/test_config.py`):
- Test default configuration exists
- Test configuration can be modified
- Test configuration validation (if any)
- Test configuration categories (pins, timing, colors, animations)

**Success criteria**:
- All configurable parameters from spec.md are present
- Easy to understand and modify
- Tests pass

---

### Step 2: Universe Code Manager
**Goal**: Pure logic for universe code operations

**Files to create**:
- `universe_code.py` - UniverseCode class

**Tests** (`tests/test_universe_code.py`):
- Test parsing "C137" → letter='C', number=137
- Test formatting letter='C', number=137 → "C137"
- Test increment: C137→C138, C999→D000, F999→A000
- Test decrement: C137→C136, C000→B999, A000→F999
- Test valid letter range (A-F)
- Test valid number range (0-999)
- Test edge cases (all boundaries)
- Test display format (always 4 characters)

**Success criteria**: All universe code logic works correctly, tests pass

---

### Step 3: Hardware Abstraction Layer
**Goal**: Mockable interface to all hardware components

**Files to create**:
- `hardware.py` - Hardware manager with abstract interfaces

**Interfaces needed**:
- `LEDController` - Control 3 LEDs with brightness (active-LOW logic)
- `DisplayController` - Wrapper around tm1637 for our use cases
- `NeopixelController` - Manage 15-pixel RGB strip
- `EncoderReader` - Read encoder state
- `ButtonReader` - Read button state with interrupts

**Tests** (`tests/test_hardware.py`):
- Test LED brightness setting (verify active-LOW inversion)
- Test LED individual control
- Test display text/number display
- Test display brightness
- Test neopixel color setting
- Test neopixel buffer update
- Test encoder reading
- Test button state reading
- Test hardware initialization
- Test error handling (failed initialization)

**Success criteria**:
- All hardware mockable for testing
- Tests pass with mocks
- Error handling for failed initialization

---

### Step 4: Animation Engine
**Goal**: Time-based neopixel animations with additive compositing

**Files to create**:
- `animations.py` - Animation classes and compositor

**Animation classes needed**:
- `Animation` (base class)
- `GentleMotionAnimation` - Smooth wave effect
- `SparkleAnimation` - Random sparkles in groups
- `RampUpAnimation` - Ramping up for portal generation
- `ThrombAnimation` - Portal generation throbbing
- `AnimationCompositor` - Additive blending with clamping

**Tests** (`tests/test_animations.py`):
- Test animation base class
- Test gentle motion: single pixel, decay curve, timing
- Test sparkle: random timing, groups, brightness
- Test ramp up: center pixel, spreading, timing offset
- Test throb: spreading formula, oscillation
- Test compositor: additive blending, clamping at 255
- Test animation lifecycle (start, update, finished)
- Test controllable time for deterministic testing

**Success criteria**:
- All animations work correctly in isolation
- Compositor properly combines animations
- Tests pass with mock time

---

### Step 5: Input Handler
**Goal**: Process encoder/button events with long press detection and idle timeout

**Files to create**:
- `input_handler.py` - InputHandler class

**Features needed**:
- Encoder change detection (increment/decrement)
- Button press detection via interrupts
- Long press detection (configurable threshold)
- Short press detection
- Idle timeout tracking
- Event queue or callback system

**Tests** (`tests/test_input_handler.py`):
- Test encoder clockwise detection
- Test encoder counterclockwise detection
- Test short button press (<700ms)
- Test long button press (≥700ms)
- Test idle timeout (3 minutes default)
- Test idle reset on input
- Test long press threshold configuration
- Test button press during encoder rotation
- Test event handling/callbacks

**Success criteria**:
- Reliable input detection
- Long press timing accurate
- Idle timeout works correctly
- Tests pass

---

### Step 6: State Machine
**Goal**: Manage mode transitions and coordinate system behavior

**Files to create**:
- `state_machine.py` - StateMachine class with State classes

**States needed**:
- `StandbyState`
- `OperationState`
- `UniverseCodeEditState`
- `PortalGeneratingState` (with sub-phases)

**Tests** (`tests/test_state_machine.py`):
- Test initial state (Standby)
- Test Standby → Operation (long press)
- Test Operation → Standby (idle timeout)
- Test Operation → UniverseCodeEdit (short press)
- Test Operation → PortalGenerating (long press)
- Test UniverseCodeEdit → Operation (complete)
- Test UniverseCodeEdit → Operation (abort via long press)
- Test PortalGenerating → Operation (complete sequence)
- Test universe code increment/decrement in Operation mode
- Test universe code editing in UniverseCodeEdit mode
- Test state entry/exit actions
- Test invalid state transitions

**Success criteria**:
- All state transitions work correctly
- Each state's behavior matches spec
- Tests pass

---

### Step 7: Main Coordinator
**Goal**: Tie everything together with initialization and main loop

**Files to create**:
- `main.py` - Main application

**Features needed**:
- Hardware initialization with error handling
- Error code display (LED flashing)
- State machine initialization
- Main loop:
  - Process input events
  - Update state machine
  - Update animations
  - Render to hardware
  - Maintain consistent timing
- Graceful error handling

**Tests** (`tests/test_integration.py`):
- Test successful initialization
- Test initialization with display failure
- Test initialization with neopixel failure
- Test error code display
- Test main loop one iteration
- Test mode transitions via inputs
- Test animation rendering
- Test timing consistency

**Success criteria**:
- System initializes correctly
- Error handling works
- Main loop runs smoothly
- Tests pass

---

### Step 8: Hardware Testing Utilities
**Goal**: Easy hardware verification on device

**Files to create** (optional, for your convenience):
- `hardware_verify.py` - Interactive hardware test menu

**Features**:
- Test each component individually
- Test mode sequences
- Test animations
- Useful for debugging on actual hardware

**Tests**: Manual verification on hardware

**Success criteria**: Easy to diagnose hardware issues in the field

---

## Testing Strategy

### Unit Tests
- Each module tested in isolation
- Use mocks for hardware dependencies
- Focus on logic correctness

### Integration Tests
- Test interactions between modules
- Test complete workflows
- Use mocks for hardware

### Hardware Tests
- Run on actual Pico W hardware
- Verify physical behavior
- Use existing hardware_tests/ as reference

## Development Workflow

For each step:
1. **Write tests first** - Define expected behavior
2. **Run tests** - Verify they fail (no implementation yet)
3. **Implement** - Write minimal code to pass tests
4. **Run tests** - Verify they pass
5. **Refactor** - Clean up code if needed
6. **Commit** - Save progress with descriptive message

## Configuration Management

All configurable parameters organized in `config.py`:

```python
class Config:
    # Pin assignments
    PINS = {...}

    # Timing parameters
    TIMING = {...}

    # Color parameters
    COLORS = {...}

    # Animation parameters
    ANIMATIONS = {...}

    # Hardware parameters
    HARDWARE = {...}
```

## Future Extensions

The architecture supports:
- **Settings mode**: Add new state for runtime configuration
- **Additional animations**: Extend animation classes
- **New error codes**: Add to error handler
- **Logging**: Add optional debug output
- **Persistence**: Save universe code to flash

## Questions Before Starting

Before implementation begins, please confirm:

1. **Testing approach**: Is local testing with mocks acceptable, or do you prefer running tests directly on the Pico W?

Unit tests should be run locally with mocks, so that development can be done without my needing to be there to fiddle with the hardware. If you can, you can create a mechanism to run the tests on the hardware itself, but this is not required. If automated tests pass locally, we can move to integration testing on the device. Note that the code in the `hardware_tests` directory has been demonstrated to work on the hardware. 

2. **File organization**: Is the proposed structure (separate modules vs. monolithic main.py) acceptable?

Looks good.

3. **Step order**: Should we proceed in the order listed, or prioritize certain modules?

The suggested order is fine.

4. **Test framework**: Should we use a specific test framework (unittest, pytest) or simple assert statements?

I am familiar with pytest, but I haven't done a MicroPython project before, so I leave the choice to you.

5. **Universe code persistence**: Should the last-selected universe code be saved to flash and restored on power-up, or always start at C137?

Since we have no power switch, we are working on the idea that the device runs all day, going into standby mode to save battery as much as possible. So there is no need to persist the universe code in flash.

6. **Error recovery**: If hardware init fails, should the device retry, or just show error codes and halt?

Show error codes but continue to run as far as possible otherwise. LEDs are off except in portal generation, so it will be easy to see them. You could turn off error codes in standby mode, though.

7. **Animation timing**: Should animations use time.ticks_ms() for timing, or frame-based counting?

I've no opinion. Again, I've never done a MicroPython project on a microcontroler before. Smooth motion is desirable.

8. **Brightness range**: For LEDs and neopixels, should brightness be 0-100 (percentage) or 0-255 (byte)?

For readability I'm inclined to go for a percentage.


# Other comments on the plan

* It talks about a 15-pixel strip of neopixels. The number must be configurable.
* Somewhere in there was a name with “Thromb” in it; that should be corrected to “Throb”.
* Not sure whether this is consistent with your architecture, but I would be inclined to have a layer that manages the brightness of each pixel and each LED that abstracts them. For example, each of the animations could be given an array of values for the brightnesses/colours of each, and the abstraction layer handles adding them together to control the hardware. Also, each pixel/LED could have a queue of timed changes from each client (new brightness/colour; time to change; perhaps a blending function eg, linear, quadratic), and an optional callback to say when the queue has been emptied. This might make the animation code rather simpler. However, these are suggestions, not requirements: please make something effective and straightforward to write, test and work with.
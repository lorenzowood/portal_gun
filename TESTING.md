# Portal Gun Testing Guide

## Test Status

**All 134 tests passing!** ✓

- 18 tests - Mock infrastructure
- 12 tests - Configuration
- 34 tests - Universe code manager
- 23 tests - Hardware abstraction
- 18 tests - Animation engine
- 12 tests - Input handler
- 17 tests - State machine

## Running Tests Locally

Tests run on your development machine without hardware using mocks:

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_universe_code.py -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

## Testing on Hardware

### 1. Upload Files to Pico

Upload these files to your Raspberry Pi Pico W:

**Required files:**
- `main.py` - Main controller (auto-runs on power-up)
- `config.py` - Configuration
- `hardware.py` - Hardware abstraction
- `state_machine.py` - State machine
- `input_handler.py` - Input handling
- `universe_code.py` - Universe code logic
- `animations.py` - Animation engine
- `tm1637.py` - Display driver (already present)

**Note:** Do NOT upload the `tests/` directory to the Pico - tests run on your computer.

### 2. Component Testing

Test individual components using the existing hardware test files:

```bash
# Test LEDs (should show smooth wave animation)
# Upload and run: hardware_tests/led_test.py

# Test button (should toggle LED on press)
# Upload and run: hardware_tests/button_test.py

# Test display (should count up on button press)
# Upload and run: hardware_tests/display_test.py

# Test encoder (should show dimension counter)
# Upload and run: hardware_tests/encoder_test.py

# Test neopixels (should show rainbow pattern)
# Upload and run: hardware_tests/pixel_test.py
```

### 3. Full System Test

Once `main.py` is uploaded as the main file:

**Power-on:**
- Display should show "Stby" for 3 seconds
- All lights should be off

**Standby → Operation:**
- Long press button (700ms)
- Display should show "C137"
- Neopixels should start gentle background animation

**Universe Code Adjustment:**
- Turn encoder clockwise → C138, C139...
- Turn encoder counter-clockwise → C136, C135...

**Universe Code Edit Mode:**
- Short press button
- Display shows "C" flashing
- Turn encoder to change letter
- Short press to move to next digit
- Repeat for all 4 characters
- Long press to abort and restore original

**Portal Generation:**
- Long press button (from Operation mode)
- Should run through 4 phases:
  1. Prepare (500ms) - display flashes
  2. Ramp up (1s) - neopixels ramp up
  3. Generate (3s) - full effect
  4. Ramp down (2s) - fade out
- Returns to Operation mode

**Idle Timeout:**
- Wait 3 minutes with no input
- Should return to Standby mode

### 4. Error Code Testing

If hardware fails to initialize:

**Display failure** (1 flash):
- Center LED flashes once, pauses, repeats

**Neopixel failure** (2 flashes):
- Center LED flashes twice, pauses, repeats

**Multiple failures**:
- Cycles through all error codes

## Configuration Tuning

All timing and behavior parameters are in `config.py`. To adjust:

1. Edit `config.py` on your computer
2. Re-upload to the Pico
3. Power cycle or press reset

Common adjustments:
- `LONG_PRESS_MS` - Long press sensitivity
- `IDLE_TIMEOUT_MS` - Time until standby
- `NUM_PIXELS` - If you have different strip length
- Animation colors and timings in `Config.ANIMATIONS` section

## Troubleshooting

### No display output
- Check `tm1637.py` is uploaded
- Verify display wiring (GP6 DIO, GP7 CLK)
- Check error codes on center LED

### Button not responding
- Verify button wiring (GP12, PULL_UP)
- Try different press durations
- Check serial output for debug messages

### Neopixels not working
- Verify neopixel wiring (GP16 data, VSYS power)
- Check `NUM_PIXELS` in `config.py` matches your strip
- Ensure 4×AA batteries provide enough current

### LEDs always on/off
- Remember: active-LOW (LOW = on)
- Check `LEDS_ACTIVE_LOW` in config.py
- Verify wiring (GP13, GP14, GP15)

## Serial Debugging

Connect via serial to see debug output:

```python
# In main.py, messages are printed:
# - "Portal Gun initializing..."
# - "Hardware errors: [codes]"
# - "Hardware initialized successfully"
# - "Initial universe code: C137"
# - "Portal Gun ready!"
# - "Starting main loop..."
```

## Next Steps

### TODO Items (nice-to-have enhancements):

1. **Universe Code Edit Mode Display**
   - Currently shows static code
   - Should flash the character being edited (300ms, 50% duty)

2. **Portal Generation Display Animations**
   - Prepare phase: Flash universe code 3 times
   - Ramp up: Spin letters, cycle numbers rapidly
   - Generate: Progressive lock-in of each character
   - Ramp down: Flash final code

3. **Portal Generation Neopixel Animations**
   - Full implementation of throb effect
   - Wave spreading from center
   - Proper phase transitions

4. **Portal Generation LED Effects**
   - Synchronized oscillation with neopixels
   - 20Hz noise overlay
   - Smooth ramping

5. **Settings Mode** (future)
   - Adjust parameters without re-uploading
   - Use encoder to navigate menus
   - Store settings in flash

## Architecture Notes

The codebase is modular and testable:

- **config.py** - Single source of truth for all parameters
- **hardware.py** - Mockable hardware abstraction
- **universe_code.py** - Pure logic, no hardware dependencies
- **animations.py** - Time-based with additive compositing
- **input_handler.py** - Event-based input processing
- **state_machine.py** - Clear state transitions
- **main.py** - Coordinator that ties everything together

This architecture makes it easy to:
- Test logic without hardware
- Add new states or animations
- Tune parameters
- Debug issues
- Extend functionality

All 134 tests ensure core logic is correct before hardware testing.

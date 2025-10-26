# Portal Gun Prop - Raspberry Pi Pico W

A Rick and Morty Portal Gun prop for ComicCon, built with a Raspberry Pi Pico W. Features sophisticated LED animations, universe code selection, and theatrical portal generation effects.

## Hardware

- Raspberry Pi Pico W
- 4×AA battery pack (6V)
- 3× 10mm green LEDs with 330Ω resistors
- WS2814 RGBW neopixel strip (20 pixels, RGB mode)
- TM1637 4-digit 7-segment display (red)
- KY-040 rotary encoder with push button

## Pin Connections

- **LEDs**: GP13, GP14, GP15 (active-LOW via 330Ω resistors to 3V3)
- **Neopixels**: GP18 data, VSYS power
- **TM1637 Display**: GP7 (DIO), GP8 (CLK)
- **Rotary Encoder**: GP10 (CLK), GP11 (DT), GP12 (SW button)
- **Power**: VSYS and GND from 4×AA batteries

## Functionality

### Power-On & Standby Mode

On power-up, the device enters **Standby Mode**:
- Display shows "Stby" for 3 seconds, then turns off
- All LEDs and neopixels are off to save battery
- Long press (700ms) of the encoder button activates Operation Mode

### Operation Mode

The main operating mode with background animations:
- **Display**: Shows current universe code (default: "C137")
- **Neopixels**: Gentle motion animation with occasional sparkles
- **Universe Code Selection**:
  - Turn encoder clockwise: increment (C137→C138...C999→D000...F999→A000)
  - Turn encoder counter-clockwise: decrement
- **Short press**: Enter Universe Code Edit Mode for fast editing
- **Long press**: Trigger Portal Generation sequence
- **Auto-standby**: Returns to Standby after 3 minutes of inactivity

### Universe Code Edit Mode

Fast character-by-character editing:
1. First character flashes - rotate encoder to change, press to confirm
2. Advances to next character automatically
3. Process repeats for all 4 characters
4. Display flashes twice on completion, returns to Operation Mode
5. Long press at any time cancels and returns to Operation Mode with original code

### Portal Generation Mode

Theatrical 6.5-second sequence with four phases:

**1. Prepare (500ms)**
- Neopixels continue background animation
- Display scrolls universe code off screen, then goes blank

**2. Ramp Up (1 second)**
- Neopixels: Green wave spreads from center with rapid flashing effect
- Display: Rapidly cycles through random characters (like WOPR finding codes)
- LEDs: Ramp up to full brightness

**3. Generate (3 seconds)**
- Neopixels: Rapid blue-white "portal throb" pulsing from center
- Display: Characters progressively lock in to show final universe code
- LEDs: Oscillate in sync with throb, with added noise effect

**4. Ramp Down (2 seconds)**
- Neopixels: Portal effect fades as background animation returns
- Display: Flashes final universe code
- LEDs: Fade to off
- Returns to Operation Mode

### Error Handling

If hardware fails to initialize, the center LED indicates error codes via flash patterns:
- **1 flash**: TM1637 display failed
- **2 flashes**: Neopixel strip failed

Flash rate: 3Hz (150ms on, 183ms off), with 1-second pause between codes.
Multiple errors cycle continuously.

Expected battery life: 7-10 hours on fresh alkaline AAs.

## Code Architecture

The project uses a modular architecture with the following components:

### Main Application
- **`main.py`**: Main controller that coordinates all subsystems (runs automatically on power-up)
- **`config.py`**: Centralized configuration for all timing, colors, and animation parameters

### Core Systems
- **`state_machine.py`**: State machine implementing Standby, Operation, Universe Code Edit, and Portal Generation states
- **`hardware.py`**: Hardware abstraction layer for LEDs, neopixels, display, and encoder
- **`input_handler.py`**: Interrupt-based input handling with idle timeout detection
- **`universe_code.py`**: Universe code data type with increment/decrement logic (A000-F999)

### Animation System
- **`animations.py`**: Animation compositor with gentle motion and sparkle effects
  - `AnimationCompositor`: Composites multiple animation layers
  - `GentleMotionManager`: Generates gentle green waves across neopixels
  - `SparkleGroupManager`: Creates random blue-white sparkle effects

### Library
- **`tm1637.py`**: Driver for TM1637 4-digit 7-segment display

### Hardware Test Files

Located in `/test_files/`:
- **`blink.py`**: Basic LED blink test (onboard Pico LED)
- **`led_test.py`**: Tests the three 10mm green LEDs with PWM wave animation
- **`button_test.py`**: Tests encoder push button with GPIO interrupts
- **`pixel_test.py`**: Tests neopixel strip with rainbow pattern
- **`display_test.py`**: Tests TM1637 display with button-triggered counter
- **`encoder_test.py`**: Tests rotary encoder with universe code interface

## Development

All code is written in **MicroPython**. Use VS Code with the MicroPico extension to upload and run code on the Pico W.

For detailed specifications and implementation notes, see:
- `spec.md`: Complete functional specification
- `TESTING.md`: Testing procedures and validation
- `development_sessions/`: Development session transcripts

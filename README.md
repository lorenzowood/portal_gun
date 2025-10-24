# Portal Gun Prop - Raspberry Pi Pico W

A Rick and Morty Portal Gun prop for ComicCon, built with a Raspberry Pi Pico W.

## Hardware

- Raspberry Pi Pico W
- 4×AA battery pack (6V)
- 3× 10mm green LEDs with 330Ω resistors
- WS2814 RGBW neopixel strip (30 pixels)
- TM1637 4-digit 7-segment display (red)
- KY-040 rotary encoder with push button

## Connections

- **LEDs**: GP13, GP14, GP15 (active-LOW via 330Ω resistors to 3V3)
- **Neopixels**: GP16 data, VSYS power
- **TM1637 Display**: GP6 (DIO), GP7 (CLK)
- **Rotary Encoder**: GP10 (CLK), GP11 (DT), GP12 (SW button)
- **Power**: VSYS and GND from 4×AA batteries

## Functionality

1. On power-up: Neopixels display gentle animation, display shows "C137"
2. Turn encoder clockwise: Count up (C138, C139... C999 → D000...)
3. Turn encoder counter-clockwise: Count down
4. Push button: Flash LEDs and neopixels briefly (~1 second)
5. After 2-3 minutes idle: Neopixels turn off to save battery

Expected battery life: 7-10 hours on fresh alkaline AAs.

## Hardware Test Files

### `blink.py`
Basic LED blink test using the onboard Pico LED. Verifies MicroPython is running and can control GPIO.

### `led_test.py`
Tests the three 10mm green LEDs with PWM brightness control. Creates a wave animation that sweeps across the three LEDs with gamma-corrected fading.

### `button_test.py`
Tests the KY-040 rotary encoder push button using GPIO interrupts. Toggles LED on/off when button is pressed.

### `pixel_test.py`
Tests the WS2814 neopixel strip. Displays a rainbow pattern on the first 8 pixels to verify data communication and colour rendering.

### `display_test.py`
Tests the TM1637 7-segment display. Counts up each time the button is pressed, verifying both button interrupts and display output.

### `encoder_test.py`
Tests the rotary encoder rotation detection. Turn the encoder to increment/decrement a counter displayed on the 7-segment display. Demonstrates the complete "dimension selector" interface starting at C137.

## Libraries

### `tm1637.py`
Driver for the TM1637 4-digit 7-segment display. Supports:
- `display.number(n)`: Display a number 0-9999
- `display.text(s)`: Display text (0-9, A-F, spaces)

## Programming

All code is written in MicroPython. Use VS Code with the MicroPico extension to upload and run code on the Pico W.

The main prop code should be named `main.py` to run automatically on power-up.

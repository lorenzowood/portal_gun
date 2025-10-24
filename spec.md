# Portal gun software

This is a portal gun prop for ComicCon.

## Hardware

There is a 3D-printed enclosure that mimcs the portal gun from Rick and Morty.

Inside is a Raspberry Pi Pico W powered by 4 AA cells.

The knob on the back is connected to a KY-040 rotary encoder with push button (GP10 CLK, GP11 DT, GP12 SW button).

There is a TM1637 4-digit 7-segment display in red (GP6 DIO, GP7 CLK).

There are three 10mm green LEDs on the front with 330Ω resistors (GP13, GP14, GP15, active-LOW to 3V3).

In the green translucent tube on top of the device, there is a scrunched up WS2814 neopixel strip (15 pixels RGB only, GP16 data, VSYS power) to give a chaotic look. Note: exact chip type uncertain; using RGB mode only.

## Functionality

### Overview

When power is connected, `main.py` runs, and invokes *standby mode*.

In standby mode, a long press of the knob (configurable long press time; initially 700ms) is required to put the device in *operation mode*.

If there have been no inputs for a timeout period (configurable; initially 3 minutes) the device goes back to *standby mode*.

### Standby mode

On invoking standby mode:

* The neopixels are all turned off
* The LEDs are turned off
* The 7-segment display shows “Stby” for a time (configurable; initially 3 seconds) and then goes off

A long press of the knob puts the device in operation mode.

### Operation mode

On invoking operation mode:

* The neopixels begin the *background animation*
* The LEDs are turned off
* The 7-segment display shows the last unverse code that was set (initialised to “C137”) on power-on

A short press of the button invokes *universe code edit mode*

A long press of the button invokes *portal generating mode*

Turning the knob clockwise increases the universe code. Increasing means incrementing the last three digits until you reach 999, then rolling over to 000 and incrementing the initial letter. The initial letter runs from A to F and wraps around (A→B→C→D→E→F→A). Thus incrementing from F999 gives A000.

Turning it anti-clockwise decreases the universe code. Like incrementing in reverse. Thus decrementing from A000 gives F999.

### Universe code edit mode

This is a faster way of selecting a particular universe code.

It works by editing one character of the universe code at a time.

Initially, the display goes blank and flashes the firt letter of the current universe code (configurable rate; initially 300ms, 50% duty cycle) in the first character. The flashing indicates that this letter is being edited. Turning the knob clockwise increments the letter; anticlockwise decrements it; short press of the knob fixes it and advances to the next character.

For example: on entry the universe code is C137.

The display is blank with C flashing in the first character. Rotating the knob one click clockwise changes to d. Then a short press to fix it.

Now the display reads d1 with the 1 flashing. Rotating the knob two clicks anticlockwise changes it to 9. Then a short press to fix it.

Now the display reads d93 with the 3 flashing. A short press fixes it.

Now the display reads d937 with the 7 flashing. Rotating the knob one click clockwise changes it to 8. Then a short press to fix it.

Now the display reads d938 and the whole display flashes twice, after which the device enters *operation mode*.

At any time during this process a long press of the knob aborts the edit and returns to *operation mode* with the original universe code (ie, not a partially edited one).

### Background animation

When the device is not doing portal generation, the background behaviour of the neopixels is to generate a sense of gentle motion with the odd sparkle.

This could be done with two overlapping effects applied to the neopixels. Note that any effects running should be added to each other -- eg, if one effect sets a pixel to 0,64,0 and another sets it 32,32,32, it should end up at 32,96,32, clipping at 255,255,255. The code should separate the addition method into a separate function in case we need to adjust it to avoid distracting colour shifts etc.

#### Gentle motion

Pick a random pixel. Ramp it up to 50% (configurable) green 0,255,0 (configurable) over 3 seconds (configurable), hold for 1 second (configurable), ramp it down to 0% (configurable) over 3 seconds (configurable). Also ramp up pixels either side in a decaying curve, effectively blurring this effect. Go 2 pixels (configurable) either side, and make the maximum brightness decrease by 50% (configurable) for each pixel. In this example, at maximum, we would see brightness of 12.5% 25% 50% 25% 12.5% with the chosen pixel being the third of these.

Start the next effect 5 seconds (configurable) after the start of the previous one, allowing for overlap if configured that way.

#### Sparkle

Pick a random pixel. Ramp it up to 100% (configurable) blue-white 240,240,255 (configurable) over 20ms (configurable), hold for 0ms (configurable), and ramp it down to 0% over 500ms (configurable).

The timing of each sparkle is controlled in groups. Each group has a random number between 1 (configurable) and 5 (configurable) sparkles. Within a group, the time between one sparkle and the next is random between 200ms (configurable) and 500ms (configurable).

The time between groups is between 2 seconds (configurable) and 5 seocnds (configurable)

### Portal generating mode

This mode is designed for theatrics at ComicCon, not accuracy with the show. There is no sound on the device and no projector for portal effects on a wall.

On invoking portal generation mode, the device runs a sequence:

* Preparing to fire

* Ramping up

* Generating

* Ramping down

#### Preparing to fire

Duration: 500ms (configurable)

Neopixels: continue background animation

LEDs: off

Display: flashes the unviverse code 3 times (configurable) with 50ms off and 100ms on, then leaves it on

### Ramping up

Durtion: 1s (configurable)

Neopixels: background animation stops. Centre pixel (implies we've configured how many there are) begins to ramp up to 100% (configurable) green 0,255,0 (configurable) while flashing between 50% (configurable) and 100% (configurable) of its current brightness with 10ms (configurable) at the lower brightness and 20ms (configurable) at the higher brightness.

The pixels around the centre also ramp up, starting 100ms (configurable) later for each pixel we move away from the centre.

The centre pixel reaches its full brightness at the end of ramping up. The remaining pixels ramp at the same rate and get to wherever they get to at that time.

Display: spins through the letters and rapidly through random numbers (think WOPR finding nuclear codes) every 100ms.

### Generating

Duration: 3s (configurable)

Neopixels: rapid throbbing animation around the centre pixel. By throbbing, we mean that the pixels have a background colour green 0,192,0 (configurable) and a foreground colour blue-white (240,240,255). The centre pixel is 100% foreground colour. The pixels either side “throb” by spreading the foreground colour outwards to either end of the string, so that at 100% "throb" extension they are all foreground colour, at 0% "throb" extension only the centre pixel is foreground colour and the others are background colour, and for throb extension values in between the foreground colour is mixed smoothly progressively further outwards from the centre. By way of example, using percentages to indicate how close a pixel is to foreground colour (100% = foreground, 0% = background), and with 7 pixels, we might see this:

0% throb extension:  0% 0% 0% 100% 0% 0% 0%
25% throb extension: 5% 15% 30% 100% 30% 15% 5%
50% throb extension: 20% 40% 80% 100% 80% 40% 20%
75% throb extension: 50% 75% 100% 100% 100% 75% 50%
100% throb extension: 100% 100% 100% 100% 100% 100% 100%

During generating, the throbbing ramps from 0 to 90% (configurable) in the first 100ms (configurable) and then oscillates between 90% and 40% (configurable), taking 80ms (configurable) to drop from 90% to 40% and 40ms (configurable) to get back to 90%.

LEDs: ramp up to 100% (configurable) and in 100ms (configurable) and oscillate between 100% and 50% (configurable) in sync with the throbbing of the neopixels, with an additional ±20% (configurable) of noise in the brightness applied at a frequency of 20Hz (configurable).

Display: over the duration of generating, “locks” each of the four universe code characters progressively. For example, and using * to indicate that a character is randomly cycling:

**** at 0ms
C*** at 700ms
C1** at 1400ms
C13* at 2100ms
C137 at 2800ms

Times approximate. You get the idea.

#### Ramping down

Duration: 2s (configurable)

Neopixels: the throb extension drops to 0%, at the same time as the opacity of the throbbing effect drops from 100% to 0%. At the same time, the background animation runs and its opacity ramps up from 0% to 100%, reaching 100% half way through the ramp down.

LEDs: fade to 0% brightness over the ramp down, still with the odd flicker of noise as before, and are completely off at the end.

Display: flashes the final universe code with 250ms (configurable) on and 50ms (configurable) off, until the end of ramping down, at which point the universe code is shown.

Returns to operating mode.

## Error Handling

If hardware components fail to initialize, the device will indicate errors using the center LED (assuming LEDs work, as they are least likely to fail). Error codes are communicated by flashing patterns:

- **1 flash**: TM1637 display failed to initialize
- **2 flashes**: Neopixel strip failed to initialize
- **3 flashes**: (Reserved for future errors)

Flash rate: 3Hz (150ms on, 183ms off)
Pause between error codes: 1 second
Behavior: Cycles through all active errors continuously (e.g., if both display and neopixels failed: 1 flash, pause, 2 flashes, pause, 1 flash, etc.)

## Input Handling

The rotary encoder and button use GPIO interrupts for responsive input handling. Testing has shown that interrupt-based handling provides better responsiveness than software debouncing, particularly for short button presses. No additional software debouncing is required.

## Configuration

All timing, color, and animation parameters marked as (configurable) should be easily adjustable via a centralized configuration structure to support:
- Easy tuning during development
- Potential future feature: settings mode for field adjustment of key parameters

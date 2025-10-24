from machine import Pin, PWM
import time

# Configuration
bright_intensity = 100
dim_intensity = 0
rise_time = 3000  # ms
fall_time = 3000  # ms
offset_time = 1000  # ms between LEDs

led_pin_numbers = [15, 14, 13]
leds = []

def set_intensity(pin, intensity):
    # Apply gamma correction (2.2) for perceptually linear brightness
    corrected = (intensity / 100) ** 3
    pin.duty_u16(int((1 - corrected) * 65535))

def initialise_pin_animation(led_pin_number, offset):
    led_pin = PWM(Pin(led_pin_number))
    led_pin.freq(1000)
    led = {
        "pin": led_pin,
        "start_time": time.ticks_ms() - offset
    }
    set_intensity(led["pin"], dim_intensity)
    return led

def pin_animation_tick(led):
    current_time = time.ticks_ms()
    elapsed = time.ticks_diff(current_time, led["start_time"])
    cycle_time = rise_time + fall_time
    led_time = elapsed % cycle_time
    
    if led_time <= rise_time:
        # Rising: 0 to 1
        progress = led_time / rise_time
    else:
        # Falling: 1 to 0
        time_in_fall = led_time - rise_time
        progress = 1 - (time_in_fall / fall_time)
    
    intensity = progress * (bright_intensity - dim_intensity) + dim_intensity
    set_intensity(led["pin"], intensity)

# Initialize
working_offset_time = 0
for led_pin_number in led_pin_numbers:
    leds.append(initialise_pin_animation(led_pin_number, working_offset_time))
    working_offset_time += offset_time

# Animation loop
print("LED wave animation starting...")
try:
    while True:
        for led in leds:
            pin_animation_tick(led)
        time.sleep_ms(10)  # 10ms updates = smooth animation
except KeyboardInterrupt:
    for led in leds:
        led["pin"].deinit()
    print("Stopped.")
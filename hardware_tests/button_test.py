from machine import Pin, PWM
import time

# Setup button with pull-up
button = Pin(12, Pin.IN, Pin.PULL_UP)

# Setup one LED for testing
led = PWM(Pin(15))
led.freq(1000)
led.duty_u16(65535)  # Start off

animating = False
last_press_time = 0

def button_pressed(pin):
    global animating, last_press_time
    # Debounce: ignore presses within 200ms
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_press_time) > 200:
        animating = not animating
        last_press_time = current_time
        print("Button pressed! Animating:", animating)

# Attach interrupt on falling edge (button press)
button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

print("Press button to toggle LED blinking (interrupt-driven)")
try:
    while True:
        if animating:
            led.duty_u16(0)  # On
        else:
            led.duty_u16(65535)  # Off
        time.sleep_ms(500)
        
except KeyboardInterrupt:
    led.deinit()
    print("Stopped.")
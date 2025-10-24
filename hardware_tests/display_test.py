from machine import Pin
from tm1637 import TM1637
import time

# Setup display
display = TM1637(clk=7, dio=6)

# Setup button
button = Pin(12, Pin.IN, Pin.PULL_UP)

count = 0
last_press_time = 0

def button_pressed(pin):
    global count, last_press_time
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_press_time) > 200:
        count += 1
        display.number(count)
        last_press_time = current_time
        print("Count:", count)

button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

# Initial display
display.number(count)
print("Press button to count. Current count:", count)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped.")
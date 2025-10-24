from machine import Pin
from tm1637 import TM1637
import time

# Setup display
display = TM1637(clk=7, dio=6)

# Setup encoder
clk = Pin(10, Pin.IN, Pin.PULL_UP)
dt = Pin(11, Pin.IN, Pin.PULL_UP)

# Start at C137
letter_index = 2  # C is index 2 in ABCDEF
number = 137
letters = ['A', 'B', 'C', 'D', 'E', 'F']

last_clk_state = clk.value()

def update_display():
    text = letters[letter_index] + "{:03d}".format(number)
    display.text(text)
    print(text)

def encoder_changed(pin):
    global letter_index, number, last_clk_state
    
    clk_state = clk.value()
    dt_state = dt.value()
    
    # If CLK changed from HIGH to LOW (falling edge)
    if last_clk_state == 1 and clk_state == 0:
        if dt_state == 0:
            # Clockwise - increment
            number += 1
            if number > 999:
                number = 0
                letter_index = (letter_index + 1) % 6
        else:
            # Counter-clockwise - decrement
            number -= 1
            if number < 0:
                number = 999
                letter_index = (letter_index - 1) % 6
        
        update_display()
    
    last_clk_state = clk_state

# Attach interrupt on CLK pin
clk.irq(trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, handler=encoder_changed)

# Initial display
update_display()
print("Turn encoder to change dimension. Starting at C137")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped.")
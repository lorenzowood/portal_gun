from machine import Pin
import neopixel
import time

# WS2814 are RGBW pixels (4 bytes per pixel)
# But let's try RGB mode first (3 bytes) - some libraries handle this better
num_pixels = 8
pin = Pin(18, Pin.OUT)
np = neopixel.NeoPixel(pin, num_pixels, bpp=3)  # bpp=3 for RGB

# Rainbow colours (R, G, B)
rainbow = [
    (255, 0, 0),    # Red
    (255, 127, 0),  # Orange
    (255, 255, 0),  # Yellow
    (0, 255, 0),    # Green
    (0, 0, 255),    # Blue
    (75, 0, 130),   # Indigo
    (148, 0, 211),  # Violet
    (255, 0, 255),  # Magenta
]

print("Setting rainbow colours...")
for i in range(num_pixels):
    np[i] = rainbow[i]
np.write()

print("Rainbow displayed. Press Ctrl+C to stop.")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # Turn all off
    for i in range(num_pixels):
        np[i] = (0, 0, 0)
    np.write()
    print("Stopped.")
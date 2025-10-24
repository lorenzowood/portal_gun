from machine import Pin
import time

class TM1637:
    def __init__(self, clk, dio):
        self.clk_pin = clk
        self.dio_pin = dio
        self.clk = Pin(clk, Pin.OUT)
        self.dio = Pin(dio, Pin.OUT)
        self.brightness = 7
        self._write_data_cmd()
        self._write_dsp_ctrl()
    
    def _start(self):
        self.dio.value(1)
        self.clk.value(1)
        time.sleep_us(2)
        self.dio.value(0)
    
    def _stop(self):
        self.clk.value(0)
        time.sleep_us(2)
        self.dio.value(0)
        time.sleep_us(2)
        self.clk.value(1)
        time.sleep_us(2)
        self.dio.value(1)
    
    def _write_byte(self, b):
        for i in range(8):
            self.clk.value(0)
            time.sleep_us(2)
            self.dio.value((b >> i) & 1)
            time.sleep_us(2)
            self.clk.value(1)
            time.sleep_us(2)
        
        self.clk.value(0)
        self.dio = Pin(self.dio_pin, Pin.IN)
        time.sleep_us(2)
        self.clk.value(1)
        time.sleep_us(2)
        ack = self.dio.value()
        self.dio = Pin(self.dio_pin, Pin.OUT)
        return ack == 0
    
    def _write_data_cmd(self):
        self._start()
        self._write_byte(0x40)
        self._stop()
    
    def _write_dsp_ctrl(self):
        self._start()
        self._write_byte(0x88 | self.brightness)
        self._stop()
    
    def show(self, data):
        self._write_data_cmd()
        self._start()
        self._write_byte(0xC0)
        for b in data:
            self._write_byte(b)
        self._stop()
        self._write_dsp_ctrl()
    
    # Segment patterns for 0-9 and A-F
    _SEGMENTS = {
        '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F, '4': 0x66,
        '5': 0x6D, '6': 0x7D, '7': 0x07, '8': 0x7F, '9': 0x6F,
        'A': 0x77, 'B': 0x7C, 'C': 0x39, 'D': 0x5E, 'E': 0x79, 'F': 0x71,
        'a': 0x77, 'b': 0x7C, 'c': 0x39, 'd': 0x5E, 'e': 0x79, 'f': 0x71,
        'S': 0x6D, 'T': 0x78, 'Y': 0x6E,  # S same as 5, t as |_, y as _|'
        's': 0x6D, 't': 0x78, 'y': 0x6E,  # Lowercase versions
        ' ': 0x00
    }
    
    def number(self, num):
        # Convert number to 4-digit display
        d = [0, 0, 0, 0]
        d[3] = self._SEGMENTS[str(num % 10)]
        d[2] = self._SEGMENTS[str((num // 10) % 10)]
        d[1] = self._SEGMENTS[str((num // 100) % 10)]
        d[0] = self._SEGMENTS[str((num // 1000) % 10)]
        self.show(d)
    
    def text(self, string):
        # Display a string (up to 4 characters, supports 0-9, A-F, space)
        string = string.upper()[:4]  # Take first 4 chars, uppercase
        # Pad with spaces on left to make 4 chars
        while len(string) < 4:
            string = ' ' + string
        d = [self._SEGMENTS.get(c, 0x00) for c in string]
        self.show(d)
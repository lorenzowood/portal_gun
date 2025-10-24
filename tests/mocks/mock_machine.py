"""Mock machine module for testing MicroPython code locally."""


class Pin:
    """Mock Pin class simulating MicroPython machine.Pin"""

    # Pin modes
    IN = 0
    OUT = 1
    OPEN_DRAIN = 2

    # Pull modes
    PULL_UP = 1
    PULL_DOWN = 2

    # IRQ triggers
    IRQ_FALLING = 1
    IRQ_RISING = 2
    IRQ_LOW_LEVEL = 4
    IRQ_HIGH_LEVEL = 8

    def __init__(self, pin_id, mode=OUT, pull=None):
        self.pin_id = pin_id
        self.mode = mode
        self.pull = pull
        # If pull-up, default to HIGH (1), otherwise LOW (0)
        self._value = 1 if pull == Pin.PULL_UP else 0
        self._irq_handler = None
        self._irq_trigger = None

    def value(self, val=None):
        """Get or set pin value"""
        if val is None:
            return self._value
        self._value = val
        return None

    def on(self):
        """Set pin high"""
        self._value = 1

    def off(self):
        """Set pin low"""
        self._value = 0

    def irq(self, handler=None, trigger=None):
        """Set up interrupt handler"""
        self._irq_handler = handler
        self._irq_trigger = trigger
        return self

    def _trigger_irq(self):
        """Test helper to trigger interrupt"""
        if self._irq_handler:
            self._irq_handler(self)


class PWM:
    """Mock PWM class simulating MicroPython machine.PWM"""

    def __init__(self, pin):
        self.pin = pin
        self._freq = 1000
        self._duty_u16 = 0

    def freq(self, value=None):
        """Get or set PWM frequency"""
        if value is None:
            return self._freq
        self._freq = value

    def duty_u16(self, value=None):
        """Get or set PWM duty cycle (0-65535)"""
        if value is None:
            return self._duty_u16
        self._duty_u16 = max(0, min(65535, value))

    def deinit(self):
        """Deinitialize PWM"""
        pass

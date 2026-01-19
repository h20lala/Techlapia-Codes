import logging
import time
from gpiozero import DigitalInputDevice, DigitalOutputDevice

class HX711:
    """
    A minimal pure-Python HX711 driver for Raspberry Pi 5 using gpiozero/lgpio.
    Standard 'hx711' libraries on PyPI often rely on RPi.GPIO which fails on Pi 5.
    """
    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        self.dout = DigitalInputDevice(dout_pin)
        self.pd_sck = DigitalOutputDevice(pd_sck_pin)
        self.gain = gain
        self.offset = 0
        self.reference_unit = 1
        
        # Reset
        self.reset()

    def reset(self):
        self.pd_sck.on()
        time.sleep(0.0001)
        self.pd_sck.off()
        time.sleep(0.0001)

    def is_ready(self):
        # DOUT is low when ready
        return self.dout.value == 0

    def read_raw(self):
        """
        Bit-banging the 24-bit value from HX711.
        Added explicit delays for Pi 5 stability.
        """
        while not self.is_ready():
            time.sleep(0.001)

        count = 0
        # Pulse SCK 24 times to read data
        for _ in range(24):
            # SCK High
            self.pd_sck.on()
            time.sleep(0.000001) # 1us delay
            
            # Read DOUT
            bit = 1 if self.dout.value else 0
            
            # SCK Low
            self.pd_sck.off()
            time.sleep(0.000001) # 1us delay
            
            count = (count << 1) | bit
        
        # Pulse SCK 1-3 more times for Gain selection
        pulses = 1
        if self.gain == 128:
            pulses = 1
        elif self.gain == 64:
            pulses = 3
        elif self.gain == 32:
            pulses = 2

        for _ in range(pulses):
            self.pd_sck.on()
            time.sleep(0.000001)
            self.pd_sck.off()
            time.sleep(0.000001)

        # Convert 24-bit 2's complement
        if count & 0x800000:
            count |= ~0xffffff

        return count

    def read(self):
        # Simple median filter could be added here for stability
        return self.read_raw()

    def read_average(self, times=3):
        total = 0
        for _ in range(times):
            total += self.read_raw()
        return total / times

    def get_weight(self):
        val = self.read_average(3)
        weight = (val - self.offset) / self.reference_unit
        return weight

    def tare(self, times=10):
        self.offset = self.read_average(times)
        logging.info(f"Scale tared. Offset: {self.offset}")

class ScaleSensor:
    def __init__(self, dt_pin, sck_pin, reference_unit, offset):
        self.hx = HX711(dt_pin, sck_pin)
        self.hx.reference_unit = reference_unit
        self.hx.offset = offset
        # Optional: auto-tare on startup? Maybe not, better to rely on saved config
        # But if config offset is 0, we might need to assume it's empty or force user to calibration.

    def read_weight(self):
        try:
            val = self.hx.get_weight()
            return val
        except Exception as e:
            logging.error(f"Error reading scale: {e}")
            return 0.0

    def tare(self):
        self.hx.tare()
        return self.hx.offset

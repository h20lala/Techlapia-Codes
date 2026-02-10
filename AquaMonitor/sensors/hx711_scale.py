import time
import sys
import logging

# Try importing RPi.GPIO (provided by rpi-lgpio on Pi 5)
try:
    import RPi.GPIO as GPIO
except ImportError:
    logging.error("RPi.GPIO not found. Ensure 'rpi-lgpio' is installed.")
    GPIO = None

class HX711:
    """
    HX711 driver using RPi.GPIO.
    Adapted from user-provided working script.
    """
    
    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        self.DOUT = dout_pin
        self.PD_SCK = pd_sck_pin
        self.gain = 0
        self.offset = 0          # Compatible name
        self.reference_unit = 1  # Compatible name
        
        if GPIO:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            GPIO.setup(self.PD_SCK, GPIO.OUT)
            GPIO.setup(self.DOUT, GPIO.IN)
        
        self.set_gain(gain)
        time.sleep(0.5)

    def reset(self):
        self.power_down()
        self.power_up()
    
    def set_gain(self, gain):
        if gain == 128:
            self.gain = 1
        elif gain == 64:
            self.gain = 3
        elif gain == 32:
            self.gain = 2
        
        if GPIO:
            GPIO.output(self.PD_SCK, False)
        self.read_raw()
    
    def is_ready(self):
        if not GPIO: return False
        return GPIO.input(self.DOUT) == 0
    
    def wait_ready(self, timeout=5):
        start = time.time()
        while not self.is_ready():
            if time.time() - start > timeout:
                return False
            time.sleep(0.001)
        return True
    
    def read_raw(self):
        if not self.wait_ready():
            return 0
        
        data = 0
        for _ in range(24):
            GPIO.output(self.PD_SCK, True)
            data = (data << 1) | GPIO.input(self.DOUT)
            GPIO.output(self.PD_SCK, False)
        
        # Set channel and gain for next reading
        for _ in range(self.gain):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)
        
        # Convert to signed value (24-bit 2's complement)
        if data & 0x800000:
            data -= 0x1000000
        
        return data
    
    def read(self):
        return self.read_raw()
        
    def read_median(self, times=5):
        readings = []
        for _ in range(times):
            readings.append(self.read_raw())
        readings.sort()
        mid = len(readings) // 2
        if len(readings) % 2 == 0:
            return (readings[mid-1] + readings[mid]) / 2
        else:
            return readings[mid]

    def read_average(self, times=10):
        # User script uses simple average
        total = 0
        for _ in range(times):
            total += self.read_raw()
        return total / times
    
    def get_weight(self):
        # Compatible wrapper for main.py
        val = self.read_median(5) # Use median for stability
        weight = (val - self.offset) / self.reference_unit
        return weight
    
    def tare(self, times=15):
        self.offset = self.read_average(times)
        logging.info(f"Scale tared. Offset: {self.offset}")

    def power_down(self):
        if GPIO:
            GPIO.output(self.PD_SCK, False)
            GPIO.output(self.PD_SCK, True)
        time.sleep(0.0001)
    
    def power_up(self):
        if GPIO:
            GPIO.output(self.PD_SCK, False)
        time.sleep(0.0005)

class ScaleSensor:
    def __init__(self, dt_pin, sck_pin, reference_unit, offset):
        self.hx = HX711(dt_pin, sck_pin)
        self.hx.reference_unit = reference_unit
        self.hx.offset = offset

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

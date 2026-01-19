from .ads1115 import ADCSensor
import logging

class PHSensor:
    def __init__(self, channel, slope, intercept):
        self.channel = channel
        self.slope = slope
        self.intercept = intercept
        self.adc = ADCSensor()

    def read_ph(self):
        """
        Reads voltage from ADC and converts to pH.
        """
        voltage = self.adc.read_voltage(self.channel)
        
        # pH Calculation: y = mx + c
        # m = slope, c = intercept
        ph_value = (self.slope * voltage) + self.intercept
        
        # Clamp typical physical limits 0-14
        ph_value = max(0.0, min(14.0, ph_value))
        
        return ph_value, voltage

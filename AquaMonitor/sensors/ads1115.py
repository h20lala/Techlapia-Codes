import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import logging

class ADCSensor:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ADCSensor, cls).__new__(cls)
            cls._instance.i2c = None
            cls._instance.ads = None
            cls._instance.initialized = False
        return cls._instance

    def initialize(self):
        if self.initialized:
            return
        
        try:
            # Create the I2C bus
            self.i2c = busio.I2C(board.SCL, board.SDA)
            # Create the ADC object using the I2C bus
            self.ads = ADS.ADS1115(self.i2c)
            self.initialized = True
            logging.info("ADS1115 ADC initialized successfully.")
        except Exception as e:
            logging.error(f"Failed to initialize ADS1115: {e}")
            self.ads = None

    def read_voltage(self, channel_num):
        """
        Reads voltage from a specified channel (0-3).
        """
        if not self.initialized or self.ads is None:
            logging.warning("ADS1115 not initialized. Returning 0.0")
            return 0.0
        
        try:
            if channel_num == 0:
                chan = AnalogIn(self.ads, ADS.P0)
            elif channel_num == 1:
                chan = AnalogIn(self.ads, ADS.P1)
            elif channel_num == 2:
                chan = AnalogIn(self.ads, ADS.P2)
            elif channel_num == 3:
                chan = AnalogIn(self.ads, ADS.P3)
            else:
                raise ValueError("Invalid channel number. Must be 0-3.")
            
            return chan.voltage
        except Exception as e:
            logging.error(f"Error reading ADC channel {channel_num}: {e}")
            return 0.0

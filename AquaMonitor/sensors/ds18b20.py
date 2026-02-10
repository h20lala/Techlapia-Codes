from w1thermsensor import W1ThermSensor, Sensor
import logging

class TempSensor:
    def __init__(self):
        self.sensor = None
        self.initialize()

    def initialize(self):
        try:
            # Connect to the first available DS18B20 sensor
            self.sensor = W1ThermSensor()
            logging.info(f"DS18B20 initialized. ID: {self.sensor.id}")
        except Exception as e:
            logging.error(f"Failed to initialize DS18B20: {e}")
            self.sensor = None

    def read_temperature(self):
        """
        Reads temperature in Celsius.
        """
        if self.sensor is None:
            # Try to re-initialize if it failed previously (e.g. sensor plugged in later)
            self.initialize()
            if self.sensor is None:
                return -273.15 # Error value
        
        try:
            temp_c = self.sensor.get_temperature()
            return temp_c
        except Exception as e:
            logging.error(f"Error reading temperature: {e}")
            return -273.15

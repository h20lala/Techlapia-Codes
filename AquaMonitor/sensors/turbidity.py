from .ads1115 import ADCSensor
import logging

class TurbiditySensor:
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADCSensor()

    def read_turbidity(self):
        """
        Reads voltage and converts to NTU (Nephelometric Turbidity Units).
        Note: The conversion formula is highly specific to the sensor's calibration curve.
        DFRobot Gravity Turbidity sensor usually outputs:
        - High voltage (~4.2V) for clear water.
        - Low voltage for dirty water.
        """
        voltage = self.adc.read_voltage(self.channel)
        
        # Simplified conversion for generic Gravity sensor
        # Many users use a piecewise function or polynomial.
        # Example from common DFRobot wiki (for approx reference):
        # NTU = -1120.4*V^2 + 5742.3*V - 4352.9
        # BUT this is for 5V vRef. Pi ADS1115 usually at 3.3V or 5V VDD.
        # We will return Raw Voltage + a qualitative "Level" for now,
        # and a placeholder NTU calculation.
        
        ntu = 0.0
        if voltage < 2.5: # Very turbid
            ntu = 3000.0
        elif voltage > 4.2: # Very clear
            ntu = 0.0
        else:
            # Linear approx between 4.2V(0 NTU) and 2.5V(3000 NTU)
            # Slope = (3000 - 0) / (2.5 - 4.2) = 3000 / -1.7 = -1764.7
            slope = -1764.7
            ntu = slope * (voltage - 4.2)
            
        return max(0.0, ntu), voltage

import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensors.ads1115 import ADCSensor
import config

def calibrate_turbidity():
    adc = ADCSensor()
    adc.initialize()
    
    print("Turbidity Sensor Check")
    print("----------------------")
    print("This script reads the raw voltage from the turbidity sensor.")
    print("1. Place sensor in PURE WATER (0 NTU). Note the voltage (max voltage).")
    print("2. Place sensor in DIRTY WATER (e.g., 3000 NTU). Note the voltage.")
    print("\nPress Ctrl+C to stop.\n")
    
    try:
        while True:
            v = adc.read_voltage(config.CHANNEL_TURBIDITY)
            print(f"Voltage: {v:.4f} V")
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nDone.")
        print("Update calculation logic in 'sensors/turbidity.py' based on these values.")

if __name__ == "__main__":
    calibrate_turbidity()

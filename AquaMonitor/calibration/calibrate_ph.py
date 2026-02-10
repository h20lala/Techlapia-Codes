import sys
import os
import time

# Add parent directory to path to import config and sensors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensors.ads1115 import ADCSensor
import config

def calibrate_ph():
    adc = ADCSensor()
    adc.initialize()
    
    print("pH Sensor Calibration (2-Point)")
    print("-------------------------------")
    print("This will calculate the Slope and Intercept.")
    print("You need two buffer solutions (e.g., 4.0 and 7.0).")
    
    input("Step 1: Place probe in BUFFER 1 (e.g., pH 7.0). Rinse with distilled water first.\nPress Enter when ready...")
    
    print("Reading... wait for stability (5 seconds)")
    time.sleep(5)
    
    # Average 10 readings
    total_v = 0
    for _ in range(10):
        v = adc.read_voltage(config.CHANNEL_PH)
        total_v += v
        time.sleep(0.1)
    v1 = total_v / 10
    print(f"Voltage 1: {v1:.4f} V")
    
    ph1 = float(input("Enter the pH value of Buffer 1 (e.g., 7.0): "))
    
    # ------------------
    
    input("\nStep 2: Rinse probe. Place in BUFFER 2 (e.g., pH 4.0).\nPress Enter when ready...")
    
    print("Reading... wait for stability (5 seconds)")
    time.sleep(5)
    
    total_v = 0
    for _ in range(10):
        v = adc.read_voltage(config.CHANNEL_PH)
        total_v += v
        time.sleep(0.1)
    v2 = total_v / 10
    print(f"Voltage 2: {v2:.4f} V")
    
    ph2 = float(input("Enter the pH value of Buffer 2 (e.g., 4.0): "))
    
    # Calculate Slope and Intercept
    # ph = m * v + c
    # m = (ph2 - ph1) / (v2 - v1)
    
    if v2 == v1:
        print("Error: Voltages are identical. Check wiring or probe.")
        return

    slope = (ph2 - ph1) / (v2 - v1)
    intercept = ph1 - (slope * v1)
    
    print("\nCalibration Results:")
    print(f"Slope: {slope:.4f}")
    print(f"Intercept: {intercept:.4f}")
    print("\nUpdate these values in 'config.py'.")

if __name__ == "__main__":
    calibrate_ph()

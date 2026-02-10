import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensors.hx711_scale import HX711
import config

def calibrate_scale():
    print("Scale Calibration")
    print("-----------------")
    
    hx = HX711(config.PIN_HX711_DT, config.PIN_HX711_SCK)
    
    input("Step 1: Remove all weight from scale.\nPress Enter to Tare...")
    
    hx.tare()
    offset = hx.offset
    print(f"Tare Offset: {offset}")
    
    input("\nStep 2: Place a KNOWN weight on the scale.\nPress Enter when ready...")
    
    print("Reading...")
    raw_val = hx.read_average(10)
    print(f"Raw Value (minus offset): {raw_val - offset}")
    
    known_weight = float(input("Enter the known weight (in grams/kg): "))
    
    if known_weight == 0:
        print("Weight cannot be zero.")
        return

    # reference_unit = (raw_val - offset) / known_weight
    # Because get_weight = (raw - offset) / ref
    # So ref = (raw - offset) / weight
    
    reference_unit = (raw_val - offset) / known_weight
    
    print("\nCalibration Results:")
    print(f"REFERENCE_UNIT: {reference_unit:.4f}")
    print(f"OFFSET: {offset}")
    print("\nUpdate these values in 'config.py'.")

if __name__ == "__main__":
    calibrate_scale()

import sys
import os
import time

# Add parent directory to path to import config and sensors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensors.hx711_scale import HX711
import config

def debug_scale():
    print("DEBUG: Raw Scale Readings")
    print("-------------------------")
    print("1. This script prints the raw integer value from the HX711.")
    print("2. It checks if the value changes when you press on the scale.")
    print("3. If values are constantly 0 or -1, check wiring.")
    print("4. If values don't change when you press, check Load Cell mounting.")
    print("\nPress Ctrl+C to stop.\n")
    
    hx = HX711(config.PIN_HX711_DT, config.PIN_HX711_SCK)
    
    # Force reset
    hx.reset()
    
    try:
        while True:
            # Check Ready
            ready = hx.is_ready()
            
            if ready:
                # Read Raw
                val = hx.read_raw()
                print(f"Ready: {ready} | Raw Value: {val}")
            else:
                print(f"Ready: {ready} | Waiting...")
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nDebug stopped.")

if __name__ == "__main__":
    debug_scale()

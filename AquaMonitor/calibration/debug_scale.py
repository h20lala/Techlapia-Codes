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
                hex_val = val & 0xFFFFFF
                
                print(f"Ready: {ready} | Raw (Dec): {val} | Raw (Hex): {hex_val:06X}")
                
                if val == -8388608:
                    print("  [!] ALERT: NEGATIVE SATURATION DETECTED")
                    print("      The sensor is reading the minimum possible value.")
                    print("      CAUSE: The 'Signal' wires (Green/White) are likely reversed.")
                    print("      FIX: Swap the Green and White wires on the HX711 module.")
                    print("      (Even if color-coded, internal load cell wiring can vary!)")
                elif val == 8388607:
                    print("  [!] ALERT: POSITIVE SATURATION DETECTED")
                    print("      The sensor is reading the maximum possible value.")
                    print("      CAUSE: Input voltage too high or short circuit.")
                elif val == -1 or hex_val == 0xFFFFFF:
                    print("  [!] ALERT: SENSOR DISCONNECTED OR POWER DOWN")
                    print("      Reading all 1s. Check VCC/GND/DT/SCK wiring.")
            else:
                print(f"Ready: {ready} | Waiting...")
                
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nDebug stopped.")

if __name__ == "__main__":
    debug_scale()

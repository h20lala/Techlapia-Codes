import sys
import os
import time

# Add parent directory to path to import config and sensors
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensors.hx711_scale import ScaleSensor
import config

def test_scale():
    print("Testing Calibrated Scale")
    print("------------------------")
    print(f"Using Config Values:")
    print(f"  REFERENCE_UNIT: {config.SCALE_REFERENCE_UNIT}")
    print(f"  OFFSET: {config.SCALE_OFFSET}")
    print(f"  DT Pin: {config.PIN_HX711_DT}")
    print(f"  SCK Pin: {config.PIN_HX711_SCK}")
    print("\nPress Ctrl+C to stop.\n")

    # Initialize Sensor with config values
    scale = ScaleSensor(config.PIN_HX711_DT, config.PIN_HX711_SCK, 
                        config.SCALE_REFERENCE_UNIT, config.SCALE_OFFSET)

    try:
        while True:
            # Read weight
            weight = scale.read_weight()
            
            # Print
            print(f"Weight: {weight:.2f}")
            
            time.sleep(0.5)
            
    except KeyboardInterrupt:
        print("\nTest stopped.")

if __name__ == "__main__":
    test_scale()

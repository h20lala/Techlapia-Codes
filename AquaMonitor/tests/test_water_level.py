import time
from gpiozero import Button

# The water level sensor is connected to Physical Pin 37, which is BCM GPIO 26
FLOAT_SWITCH_PIN = 26

print(f"Initializing Water Level Sensor on GPIO {FLOAT_SWITCH_PIN} (Physical Pin 37)...")

try:
    # Use pull_up=True because the switch is usually connected between GPIO and GND
    water_sensor = Button(FLOAT_SWITCH_PIN, pull_up=True)
    print("Initialization successful!")
except Exception as e:
    print(f"Failed to initialize: {e}")
    exit(1)

print("\nReading sensor state every 1 second. Press Ctrl+C to stop.")
print("-" * 50)

try:
    while True:
        # is_pressed returns True when the switch is closed (pin connected to GND)
        # is_pressed returns False when the switch is open (internal pull-up keeps pin HIGH)
        is_closed = water_sensor.is_pressed
        
        if is_closed:
            print("Switch State: CLOSED (Usually means float is UP / Water is FULL)")
        else:
            print("Switch State: OPEN   (Usually means float is DOWN / Water is LOW)")
            
        time.sleep(1)
        
except KeyboardInterrupt:
    print("\nTest stopped.")
finally:
    water_sensor.close()

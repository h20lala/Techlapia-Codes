import time
import sys
from gpiozero import Servo

# Servo Pins (Hardware PWM capable on RPi 5, matching feeder2.py)
SERVO1_PIN = 13  # Physical Pin 33
SERVO2_PIN = 12  # Physical Pin 32

print("Initializing Servos on BCM 12 and 13...")
try:
    # Initialize Servos using gpiozero with calibrated pulse widths
    servo1 = Servo(SERVO1_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    servo2 = Servo(SERVO2_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
except Exception as e:
    print(f"Failed to initialize servos: {e}")
    sys.exit(1)

def test_servo(servo, name):
    print(f"\n--- Testing {name} ---")
    
    print(f"Setting {name} to MIN (approx 0 degrees)")
    servo.value = -1.0
    time.sleep(1.5)
    
    print(f"Setting {name} to MID (approx 90 degrees)")
    servo.value = 0.0
    time.sleep(1.5)
    
    print(f"Setting {name} to MAX (approx 180 degrees)")
    servo.value = 1.0
    time.sleep(1.5)
    
    print(f"Resetting {name} to MIN")
    servo.value = -1.0
    time.sleep(1.5)
    
    # Detach signal to prevent jitter
    servo.value = None

try:
    print("Starting Servo Test Sequence...")
    test_servo(servo1, "Servo 1 (Pin 13 / Phys 33)")
    test_servo(servo2, "Servo 2 (Pin 12 / Phys 32)")
    print("Servo Test Complete!")
    
except KeyboardInterrupt:
    print("\nTest interrupted by user.")
finally:
    # Always clean up
    servo1.close()
    servo2.close()
    print("Pins released safely.")

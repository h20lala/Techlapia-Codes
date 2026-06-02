import time
import sys
from gpiozero import Servo
from hx711 import HX711  # Standard Python HX711 library

# --- PIN CONFIGURATIONS (Adjusted to avoid conflict with your docx file) ---
# HX711 Pins
DOUT_PIN = 27  # Physical Pin 13
CLK_PIN = 22   # Physical Pin 15

# Servo Pins (Using hardware PWM capable pins on RPi 5)
SERVO1_PIN = 12  # Physical Pin 33
SERVO2_PIN = 13  # Physical Pin 32

# --- SYSTEM INITIALIZATION ---
# Calibration factor from your Arduino setup
CALIBRATION_FACTOR = -1550.0
target_weight = 0.0

print("HX711 + 2 Servo System (Raspberry Pi 5)")
print("---------------------------------------")

# Initialize HX711 Weight Sensor
# Note: implementation handles may vary slightly depending on the exact hx711 package variety
hx = HX711(dout=DOUT_PIN, pd_sck=CLK_PIN)
hx.set_reference_unit(CALIBRATION_FACTOR)
hx.reset()
hx.tare()
print("Scale Tared.")

# Initialize Servos using gpiozero
# (Adjust min_pulse_width and max_pulse_width if your specific servos don't reach full 90 degrees)
# Initialize Servos using gpiozero with calibrated pulse widths for a 180-degree servo
servo1 = Servo(SERVO1_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
servo2 = Servo(SERVO2_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

# Close both servos initially (gpiozero uses a range of -1 to 1; -1 is roughly 0 degrees/closed)
servo1.value = -1.0
servo2.value = -1.0
time.sleep(1.0)
servo1.value = None  # Cut Signal!
servo2.value = None  # Cut Signal!


def run_process():
    print("Opening Servo 1 to 75 degrees...")
    servo1.value = -0.17  # Exactly 75 degrees
    time.sleep(0.5)       
    servo1.value = None   # Cut the signal to prevent jitter
    
    while True:
        weight = hx.get_weight(10)
        
        if weight < 0:
            weight = 0.0
            
        print(f"Weight: {weight:.2f} g")
        
        if weight >= target_weight:
            print("Target reached!")
            break
            
        time.sleep(0.3)
        
    print("Closing Servo 1 back to 0 degrees...")
    servo1.value = -1.0  # -1.0 is exactly 0 degrees
    time.sleep(1.0)
    servo1.value = None  
    
    print("Waiting 5 seconds...")
    time.sleep(5.0)
    
    print("Opening Servo 2 to 75 degrees...")
    servo2.value = -0.17  # Exactly 75 degrees
    time.sleep(0.5)
    servo2.value = None  
    
    print("Waiting 10 seconds...")
    time.sleep(10.0)
    
    print("Closing Servo 2 back to 0 degrees...")
    servo2.value = -1.0
    time.sleep(1.0)
    servo2.value = None  
    
    print("Process Complete!")


def main():
    global target_weight
    
    if len(sys.argv) > 1:
        try:
            target_weight = float(sys.argv[1])
        except ValueError:
            pass

    # Get user target input from terminal if not provided
    while target_weight <= 0:
        try:
            user_input = input("Enter target weight in grams: ")
            target_weight = float(user_input)
            if target_weight <= 0:
                print("Please enter a weight greater than 0.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            
    print(f"Target set to: {target_weight} g")
    time.sleep(2.0)
    
    # Execute the core process loop once
    run_process()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess interrupted safely by user.")
    finally:
        # Cleanup pin states safely on exit
        servo1.close()
        servo2.close()

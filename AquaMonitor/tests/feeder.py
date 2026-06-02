#!/usr/bin/env python3
import time
import sys
from gpiozero import Servo, DigitalInputDevice, DigitalOutputDevice

# --- CONFIGURATION (BCM Numbers) ---
# Physical Pin 29 -> GPIO 5
# Physical Pin 31 -> GPIO 6
# Physical Pin 11 -> GPIO 17
# Physical Pin 13 -> GPIO 27
DOUT_PIN = 5
SCK_PIN = 6
SERVO1_PIN = 17
SERVO2_PIN = 27

CALIBRATION_FACTOR = -1550.0
NUM_SAMPLES = 10
WEIGHT_THRESHOLD = 0.5

# ==========================
# HX711 CLASS
# ==========================
class HX711:
    def __init__(self, dout_pin, sck_pin):
        self.dout = DigitalInputDevice(dout_pin)
        self.sck = DigitalOutputDevice(sck_pin)
        self.offset = 0
        self.scale = 1
        self.sck.off()

    def is_ready(self):
        return not self.dout.value

    def wait_ready(self):
        while not self.is_ready():
            time.sleep(0.001)

    def read_raw(self):
        self.wait_ready()
        data = 0
        for _ in range(24):
            self.sck.on()
            time.sleep(0.000001) 
            data = (data << 1) | (1 if self.dout.value else 0)
            self.sck.off()
            time.sleep(0.000001)

        self.sck.on()
        time.sleep(0.000001)
        self.sck.off()

        if data & 0x800000:
            data -= 0x1000000
        return data

    def read_average(self, times=10):
        total = sum([self.read_raw() for _ in range(times)])
        return total / times

    def tare(self, times=15):
        self.offset = self.read_average(times)

    def get_weight(self, times=10):
        value = self.read_average(times) - self.offset
        return value / self.scale

# ==========================
# MAIN PROGRAM
# ==========================
def main():
    # Setup HX711
    hx = HX711(DOUT_PIN, SCK_PIN)
    hx.scale = CALIBRATION_FACTOR

    # Setup Servos with standard pulse widths (0.5ms to 2.5ms)
    # This prevents the 'Servo' out of range errors on some Pi 5 setups
    servo1 = Servo(SERVO1_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
    servo2 = Servo(SERVO2_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

    try:
        print("--- Initializing Systems ---")
        # Start at 0 degrees
        servo1.min()
        servo2.min()
        time.sleep(1)
        # value=None stops the PWM signal (removes buzz)
        servo1.value = None
        servo2.value = None

        print("Taring scale... Remove all weight.")
        time.sleep(1)
        hx.tare()
        print("Tare complete.\n")

        try:
            target_weight = float(input("Enter target weight in grams: "))
        except ValueError:
            print("Invalid input.")
            return

        print(f"Target: {target_weight}g. Starting process...")
        
        # OPEN SERVO 1
        print("Opening Servo 1...")
        servo1.mid() # 90 degrees

        while True:
            weight = hx.get_weight(NUM_SAMPLES)
            if abs(weight) < WEIGHT_THRESHOLD:
                weight = 0

            print(f"\rCurrent Weight: {weight:.1f} g", end="")
            sys.stdout.flush()

            if weight >= target_weight:
                print("\nTarget reached!")
                break
            time.sleep(0.1)

        # CLOSE SERVO 1
        print("Closing Servo 1...")
        servo1.min()
        time.sleep(1)
        servo1.value = None

        print("Waiting 5 seconds...")
        time.sleep(5)

        # OPEN SERVO 2
        print("Opening Servo 2...")
        servo2.mid()
        
        print("Waiting 10 seconds...")
        time.sleep(10)

        # CLOSE SERVO 2
        print("Closing Servo 2...")
        servo2.min()
        time.sleep(1)
        servo2.value = None

        print("\n--- Process complete! ---")

    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        print("Cleanup...")

if __name__ == "__main__":
    main()

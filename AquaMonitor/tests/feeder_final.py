#!/usr/bin/env python3
import time
import sys
import os

# Force the Pi 5 to use the modern lgpio driver
os.environ['GPIOZERO_PIN_FACTORY'] = 'lgpio'

try:
    from gpiozero import Servo, DigitalInputDevice, DigitalOutputDevice
except ImportError:
    print("ERROR: Missing libraries. Run: sudo apt install python3-gpiozero python3-lgpio")
    sys.exit(1)

# ==========================
# CONFIGURATION (BCM PINS)
# ==========================
# Physical 11 -> BCM 17 (Servo 1)
# Physical 13 -> BCM 27 (Servo 2)
# Physical 29 -> BCM 5  (HX711 DT)
# Physical 31 -> BCM 6  (HX711 SCK)

SERVO1_PIN = 17
SERVO2_PIN = 27
HX_DT_PIN  = 5
HX_SCK_PIN = 6

CALIBRATION_FACTOR = -1615.0
NUM_SAMPLES = 10
WEIGHT_THRESHOLD = 0.5

def status(msg):
    print(f"[STATUS] {msg}")
    sys.stdout.flush()

# ==========================
# HX711 CLASS (GPIOZERO)
# ==========================
class HX711:
    def __init__(self, dout_pin, sck_pin):
        status(f"Initializing HX711 (DT:{dout_pin}, SCK:{sck_pin})...")
        self.dout = DigitalInputDevice(dout_pin)
        self.sck = DigitalOutputDevice(sck_pin)
        self.offset = 0
        self.scale = CALIBRATION_FACTOR
        self.sck.off()

    def is_ready(self):
        return not self.dout.value

    def read_raw(self):
        # Wait for ready with a 2-second timeout
        timeout = 0
        while not self.is_ready():
            time.sleep(0.01)
            timeout += 1
            if timeout > 200:
                return None
        
        data = 0
        for _ in range(24):
            self.sck.on()
            time.sleep(0.000001) # Micro-delay for Pi 5 speed
            data = (data << 1) | (1 if self.dout.value else 0)
            self.sck.off()
            time.sleep(0.000001)

        # Pulse for channel A gain 128
        self.sck.on()
        time.sleep(0.000001)
        self.sck.off()

        if data & 0x800000:
            data -= 0x1000000
        return data

    def get_weight(self, times=10):
        count = 0
        total = 0
        while count < times:
            val = self.read_raw()
            if val is not None:
                total += val
                count += 1
            else:
                return 0.0 # Return 0 if scale is disconnected
        return (total / times - self.offset) / self.scale

# ==========================
# MAIN CONTROL LOGIC
# ==========================
def main():
    status("--- SYSTEM STARTUP ---")

    try:
        # 1. Setup Servos
        status("Attaching Servo 1...")
        s1 = Servo(SERVO1_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)
        status("Attaching Servo 2...")
        s2 = Servo(SERVO2_PIN, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

        # 2. Setup Scale
        hx = HX711(HX_DT_PIN, HX_SCK_PIN)

        # 3. Initial Servo Move (Close Position)
        status("Moving servos to START (0 degrees)...")
        s1.min()
        s2.min()
        time.sleep(1.5)
        s1.value = None # Stop PWM to prevent jitter/hum
        s2.value = None

        # 4. Tare
        status("Taring... Ensure scale is empty.")
        total = 0
        count = 0
        while count < 15:
            val = hx.read_raw()
            if val is not None:
                total += val
                count += 1
                print(f"  Progress: {count}/15", end="\r")
            else:
                status("FAILED: No signal from HX711. Check DT/SCK wiring!")
                time.sleep(1)
        
        hx.offset = total / 15
        status("Tare complete.")

        # 5. User Input
        try:
            target = float(input("\nEnter target weight in grams: "))
        except ValueError:
            status("Invalid input. Exit.")
            return

        # 6. Filling Process (Servo 1)
        status(f"Opening Servo 1 (Target: {target}g)...")
        s1.mid() # 90 degrees

        while True:
            weight = hx.get_weight(NUM_SAMPLES)
            if abs(weight) < WEIGHT_THRESHOLD: weight = 0
            
            print(f"  Current: {weight:.1f} g", end="\r")
            sys.stdout.flush()

            if weight >= target:
                status("\nTarget Weight Reached!")
                break
            time.sleep(0.05)

        status("Closing Servo 1...")
        s1.min()
        time.sleep(1)
        s1.value = None

        # 7. Dispensing Process (Servo 2)
        status("Waiting 5 seconds before dispense...")
        time.sleep(5)

        status("Opening Servo 2 (10 seconds)...")
        s2.mid()
        time.sleep(10)
        
        status("Closing Servo 2...")
        s2.min()
        time.sleep(1)
        s2.value = None

        status("--- ALL PROCESSES COMPLETE ---")

    except KeyboardInterrupt:
        status("\nManual Stop Detected.")
    except Exception as e:
        status(f"CRITICAL ERROR: {e}")
    finally:
        status("Cleaning up and exiting.")

if __name__ == "_main_":
    main()

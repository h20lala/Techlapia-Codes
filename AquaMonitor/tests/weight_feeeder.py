#!/usr/bin/env python3
import time
import sys
import RPi.GPIO as GPIO

# ============================================
# PIN DEFINITIONS (Physical Pin Numbers)
# ============================================
# We use GPIO.BOARD to match your request for Pin 11 and 13
SERVO1_PHYSICAL = 11  # Physical Pin 11 (GPIO 17)
SERVO2_PHYSICAL = 13  # Physical Pin 13 (GPIO 27)
HX711_DT_PHYSICAL = 29 # Physical Pin 29 (GPIO 5)
HX711_SCK_PHYSICAL = 31 # Physical Pin 31 (GPIO 6)

CALIBRATION_FACTOR = -1550.0
NUM_SAMPLES = 10

class HX711:
    def __init__(self, dout_pin, pd_sck_pin, gain=128):
        self.DOUT = dout_pin
        self.PD_SCK = pd_sck_pin
        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1
        
        GPIO.setup(self.PD_SCK, GPIO.OUT)
        GPIO.setup(self.DOUT, GPIO.IN)
        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128: self.GAIN = 1
        elif gain == 64: self.GAIN = 3
        elif gain == 32: self.GAIN = 2
        GPIO.output(self.PD_SCK, False)
        self.read_raw()

    def is_ready(self):
        return GPIO.input(self.DOUT) == 0

    def read_raw(self):
        while not self.is_ready():
            time.sleep(0.01)
        data = 0
        for _ in range(24):
            GPIO.output(self.PD_SCK, True)
            data = (data << 1) | GPIO.input(self.DOUT)
            GPIO.output(self.PD_SCK, False)
        for _ in range(self.GAIN):
            GPIO.output(self.PD_SCK, True)
            GPIO.output(self.PD_SCK, False)
        if data & 0x800000:
            data -= 0x1000000
        return data

    def get_weight(self, times=10):
        total = sum([self.read_raw() for _ in range(times)])
        avg = total / times
        return (avg - self.OFFSET) / self.SCALE

    def tare(self, times=15):
        total = sum([self.read_raw() for _ in range(times)])
        self.OFFSET = total / times

def set_servo_angle(pwm, angle):
    """Converts 0-180 degrees to duty cycle"""
    duty = 2.5 + (angle / 180.0) * 10.0
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.4) # Wait for movement
    pwm.ChangeDutyCycle(0) # Disable signal to stop jitter

def main():
    # Use BOARD mode to reference Physical Pin numbers 11 and 13
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    
    # Setup Servos
    GPIO.setup(SERVO1_PHYSICAL, GPIO.OUT)
    GPIO.setup(SERVO2_PHYSICAL, GPIO.OUT)
    
    pwm1 = GPIO.PWM(SERVO1_PHYSICAL, 50) 
    pwm2 = GPIO.PWM(SERVO2_PHYSICAL, 50)
    pwm1.start(0)
    pwm2.start(0)

    try:
        hx = HX711(dout_pin=HX711_DT_PHYSICAL, pd_sck_pin=HX711_SCK_PHYSICAL)
        hx.SCALE = CALIBRATION_FACTOR
        
        print("System Ready. Initializing Servos (Closed Position)...")
        set_servo_angle(pwm1, 0)
        set_servo_angle(pwm2, 0)
        
        print("Taring scale...")
        hx.tare(20)
        print("Scale Tared.")

        try:
            target_weight = float(input("Enter target weight (g): "))
        except ValueError:
            print("Invalid input.")
            return

        # --- RUN PROCESS (Logic from Arduino) ---
        print("\nProcess Started: Opening Servo 1")
        set_servo_angle(pwm1, 90)

        while True:
            weight = hx.get_weight(NUM_SAMPLES)
            if weight < 0: weight = 0
            print(f"Weight: {weight:.1f} g", end="\r")

            if weight >= target_weight:
                print(f"\nTarget {target_weight}g reached!")
                break
            time.sleep(0.1)

        print("Closing Servo 1...")
        set_servo_angle(pwm1, 0)
        
        print("Waiting 5 seconds...")
        time.sleep(5)

        print("Opening Servo 2...")
        set_servo_angle(pwm2, 90)
        
        print("Waiting 10 seconds...")
        time.sleep(10)

        print("Closing Servo 2...")
        set_servo_angle(pwm2, 0)
        print("Process Complete!")

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        pwm1.stop()
        pwm2.stop()
        GPIO.cleanup()
        print("GPIO Cleaned.")

if __name__ == "_main_":
    main()

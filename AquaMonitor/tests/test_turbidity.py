from gpiozero import DigitalInputDevice
from time import sleep

# GPIO17 (physical pin 11)
sensor = DigitalInputDevice(17)

print("Turbidity sensor test started...")
print("Adjust the blue potentiometer on the module.")

while True:
    if sensor.value == 1:
        print("✅ Water CLEAR / BELOW threshold")
    else:
        print("⚠️ Water TURBID / ABOVE threshold")

    sleep(1)

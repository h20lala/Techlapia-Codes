import sys
import time
from gpiozero import OutputDevice

# --- PIN CONFIGURATION ---
# Replace with the actual GPIO pin connected to your 5V relay IN pin
RELAY_PIN = 17 # Example: GPIO 17 (Physical Pin 11)

# Initialize the relay (active_high=False if your relay module is active low, which is common for 5V Arduino relays)
# Adjust active_high if your relay works oppositely
try:
    pump_relay = OutputDevice(RELAY_PIN, active_high=False, initial_value=False)
except Exception as e:
    print(f"Error initializing relay on GPIO {RELAY_PIN}: {e}")
    sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 water_pump.py [on|off]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "on":
        print("Turning ON the water filter pump...")
        pump_relay.on()
        # To keep it running, you might just exit and let the state persist, 
        # but `gpiozero` resets state on exit unless we prevent it or use a persistent daemon.
        # Alternatively, we just loop indefinitely when ON, or use pigpio.
        # For a simple script called by a server, it's better to keep the script running if it's ON,
        # or use a different library if we want to fire-and-forget.
        # Wait, gpiozero closes the pin on exit. We should just keep it alive if ON?
        # Actually, if we want to turn it ON and let it stay ON, we shouldn't exit if using gpiozero.
        # Let's loop indefinitely until killed.
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    elif command == "off":
        print("Turning OFF the water filter pump...")
        pump_relay.off()
        # State turns off automatically on exit, but we explicitly turn it off here.
    else:
        print("Invalid command. Use 'on' or 'off'.")

if __name__ == "__main__":
    main()

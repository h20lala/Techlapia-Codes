from flask import Flask, jsonify, Response
from flask_cors import CORS
import time
import random
import threading
import numpy as np
import cv2  # OpenCV for Camera

# Try to import sensor libraries (Mock if not available)
PH_MOCK = True
TURB_MOCK = True
TEMP_MOCK = True

ph_chan = None
turbidity_sensor = None
device_file = None

try:
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    from gpiozero import DigitalInputDevice
    import glob
    
    # pH Setup
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        ads.gain = 1
        ph_chan = AnalogIn(ads, ADS.P0)
        PH_MOCK = False
        print("pH sensor initialized successfully.")
    except Exception as e:
        print(f"pH sensor missing or failed: {e}")
    
    # Turbidity Setup
    try:
        turbidity_sensor = DigitalInputDevice(17)
        TURB_MOCK = False
        print("Turbidity sensor initialized successfully.")
    except Exception as e:
        print(f"Turbidity sensor missing or failed: {e}")
    
    # Temp Setup
    try:
        base_dir = '/sys/bus/w1/devices/'
        device_folders = glob.glob(base_dir + '28*')
        if device_folders:
            device_file = device_folders[0] + '/w1_slave'
            TEMP_MOCK = False
            print("Temperature sensor initialized successfully.")
        else:
            print("Temperature sensor 1-wire folder not found.")
    except Exception as e:
        print(f"Temperature sensor missing or failed: {e}")

except Exception as e:
    print(f"Sensor libraries not found or hardware missing: {e}")
    print("Running in MOCK MODE for ALL SENSORS")

app = Flask(__name__)
CORS(app) # Enable CORS for React frontend

# --- CAMERA STREAMING ---
camera = cv2.VideoCapture(0) # 0 is usually the default camera (USB or Pi Cam if configured)
if not camera.isOpened():
    print("WARNING: Camera not found or accessible. Using MOCK video feed.")
    camera = None

def generate_frames():
    while True:
        if camera is None:
            # Create a black frame with text
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, "No Camera Detected", (180, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            time.sleep(1) # Low FPS for mock
        else:
            success, frame = camera.read()
            if not success:
                # If reading fails mid-stream, just break or handle error
                # For now, break loop (stream ends)
                break
            else:
                # Encode frame to JPG
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                # Yield frame in MJPEG format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
# ------------------------

def read_temp():
    if TEMP_MOCK or not device_file:
        return round(random.uniform(25.0, 32.0), 1)
        
    try:
        with open(device_file, 'r') as f:
            lines = f.readlines()
        if lines[0].strip()[-3:] != 'YES':
            return 0
        equals_pos = lines[1].find('t=')
        if equals_pos != -1:
            temp_string = lines[1][equals_pos+2:]
            return float(temp_string) / 1000.0
    except:
        return 0

def read_ph():
    if PH_MOCK or not ph_chan:
        return round(random.uniform(6.5, 8.5), 1)
        
    try:
        # Simple convert voltage to pH (needs calibration normally)
        # Assuming 2.5V center = pH 7
        voltage = ph_chan.voltage
        # Example formula: pH = 7 + ((2.5 - voltage) / 0.18)
        # This is a placeholder formula
        return round(7 + ((2.5 - voltage) * 3.5), 2)
    except:
        return 7.0

def read_turbidity():
    if TURB_MOCK or not turbidity_sensor:
        return round(random.uniform(0, 25), 1)
        
    try:
        # Digital sensor only returns 0 or 1 (High/Low)
        # If High (1) -> Clear (< Threshold), If Low (0) -> Turbid?
        # Script says: if sensor.value == 1: CLEAR
        # We need a value for the UI (mg/L or NTU). 
        # Since it's digital, we can only return approximate.
        # Clear = 5 NTU, Turbid = 100 NTU
        if turbidity_sensor.value == 1:
            return 5 # Clear
        else:
            return 100 # Turbid
    except:
        return 0

def read_water_level():
    # No sensor script provided for water level in the examples
    # Returning mock value
    return 75 

@app.route('/api/sensors')
def get_sensors():
    data = {
        "temperature": read_temp(),
        "ph": read_ph(),
        "turbidity": read_turbidity(),
        "water_level": read_water_level(),
        "do": 6.5, # Mock DO > 5
        "bod": 2.0, # Mock BOD < 5
        "tds": 350 # Mock TDS < 400
    }
    return jsonify(data)

if __name__ == '__main__':
    # Run threaded to allow camera loop
    app.run(host='0.0.0.0', port=5000, threaded=True)

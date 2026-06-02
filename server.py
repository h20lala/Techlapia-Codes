from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import time
import random
import threading
import numpy as np
import cv2  # OpenCV for Camera
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
import schedule

# Load Environment Variables
load_dotenv()

# Initialize Supabase
import urllib.request
import json
SUPABASE_URL = "https://qekehslduothjlhxzmbw.supabase.co"
SUPABASE_KEY = "sb_publishable_flpDIdOuSh5DNedl9wqjhw_qOfz1DZy"

# --- SQLITE DB SETUP ---
DB_FILE = 'techlapia.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            time TEXT,
            amount_g REAL,
            weight_g REAL,
            population INTEGER,
            temperature REAL,
            ph REAL,
            water_level REAL,
            turbidity REAL,
            synced INTEGER DEFAULT 0
        )
    ''')
    try:
        c.execute('ALTER TABLE logs ADD COLUMN synced INTEGER DEFAULT 0')
    except sqlite3.OperationalError:
        pass # Column already exists
        
    c.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            population INTEGER,
            length REAL,
            width REAL,
            depth REAL,
            weight REAL,
            mock_weight REAL DEFAULT 20
        )
    ''') 
    try:
        c.execute('ALTER TABLE settings ADD COLUMN mock_weight REAL DEFAULT 20')
    except sqlite3.OperationalError:
        pass # Column already exists
    # Init default settings if empty
    c.execute('SELECT COUNT(*) FROM settings')
    if c.fetchone()[0] == 0:
        c.execute('INSERT INTO settings (id, population, length, width, depth, weight) VALUES (1, 15, 172, 194, 75, 250)')
    conn.commit()
    conn.close()

init_db()

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
    from adafruit_ads1x15.ads1x15 import Pin
    from gpiozero import DigitalInputDevice
    import glob
    
    # pH Setup
    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        ads = ADS.ADS1115(i2c)
        ads.gain = 1
        ph_chan = AnalogIn(ads, Pin.A0)
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
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
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
        voltage = ph_chan.voltage
        return round(7 + ((2.5 - voltage) * 3.5), 2)
    except:
        return 7.0

def read_turbidity():
    if TURB_MOCK or not turbidity_sensor:
        return round(random.uniform(0, 25), 1)
        
    try:
        if turbidity_sensor.value == 1:
            return 5 # Clear
        else:
            return 100 # Turbid
    except:
        return 0

def read_water_level():
    return 75 

@app.route('/api/sensors')
def get_sensors():
    global last_temp_state, user_overridden, override_time, water_pump_process
    import time
    
    current_temp = read_temp()
    
    # Check 5-minute override timeout
    if user_overridden and (time.time() - override_time > 300):
        user_overridden = False
        last_temp_state = "normal" # Force re-evaluation

    # Auto water-filter logic for high temp
    if current_temp > 32:
        if last_temp_state == "normal":
            # Temp just crossed threshold to high
            if not user_overridden:
                if water_pump_process is None or water_pump_process.poll() is not None:
                    start_water_pump()
            last_temp_state = "high"
            user_overridden = False # New state transition resets override
    elif current_temp <= 32:
        if last_temp_state == "high":
            # Temp dropped back to normal
            if not user_overridden and (water_pump_process is not None and water_pump_process.poll() is None):
                stop_water_pump()
            last_temp_state = "normal"
            user_overridden = False

    filter_on = (water_pump_process is not None and water_pump_process.poll() is None)

    data = {
        "temperature": current_temp,
        "ph": read_ph(),
        "turbidity": read_turbidity(),
        "water_level": read_water_level(),
        "do": 6.5, 
        "bod": 2.0, 
        "tds": 350,
        "water_filter_on": filter_on
    }
    return jsonify(data)

# --- FEEDING AND LOGIC ---
def get_settings():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT population, length, width, depth, weight, mock_weight FROM settings WHERE id = 1')
    row = c.fetchone()
    conn.close()
    if row:
        return {"population": row[0], "length": row[1], "width": row[2], "depth": row[3], "weight": row[4], "mock_weight": row[5] if row[5] else 20}
    return {"population": 15, "length": 172, "width": 194, "depth": 75, "weight": 250, "mock_weight": 20}

def calculate_feeding():
    settings = get_settings()
    # We will use the mock current weight
    w = settings.get('mock_weight', 20)
    s = settings['population']
    
    # Table 2: Daily Feeding Ratio (%)
    if w <= 1:
        dfr_percent = 20 # Avg 10-30
    elif w <= 5:
        dfr_percent = 8  # Avg 6-10
    elif w <= 20:
        dfr_percent = 5  # Avg 4-6
    elif w <= 100:
        dfr_percent = 3.5 # Avg 3-4
    else:
        dfr_percent = 2.25 # Avg 1.5-3
        
    dfr = dfr_percent / 100.0
    
    # Table 3: Daily Feeding Frequency
    if w <= 1:
        f = 6 # Avg 4-8
    elif w <= 5:
        f = 6 # Avg 4-8
    elif w <= 20:
        f = 3 # Avg 2-4
    elif w <= 100:
        f = 3 # Avg 2-4
    else:
        f = 3 # Avg 2-4
        
    # Equation 4: A = (S x W x DFR) / f
    if f > 0:
        a = (s * w * dfr) / f
    else:
        a = 0
        
    return {"amount_g": round(a, 2), "frequency": f, "weight": w, "population": s}
def get_feeding_times(frequency):
    # Depending on frequency, map times evenly throughout the day (e.g. 9am to 6pm)
    times = []
    if frequency == 1:
        times = ["09:00"]
    elif frequency == 2:
        times = ["09:00", "15:00"]
    elif frequency == 3:
        times = ["09:00", "13:00", "17:00"]
    elif frequency == 4:
        times = ["09:00", "12:00", "15:00", "18:00"]
    elif frequency == 5:
        times = ["08:00", "10:30", "13:00", "15:30", "18:00"]
    elif frequency >= 6:
        times = ["08:00", "10:00", "12:00", "14:00", "16:00", "18:00"]
    return times

def log_feeding(amount_g, weight_g, population):
    now = datetime.now()
    date_str = now.strftime('%m/%d/%Y')  # Matches dummy data format
    time_str = now.strftime('%I:%M %p')
    temp = read_temp()
    ph = read_ph()
    lvl = read_water_level()
    turb = read_turbidity()
    
    # Local SQLite save
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO logs (date, time, amount_g, weight_g, population, temperature, ph, water_level, turbidity, synced)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)
    ''', (date_str, time_str, amount_g, weight_g, population, temp, ph, lvl, turb))
    log_id = c.lastrowid
    conn.commit()
    
    # Supabase save via REST API
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            url = f"{SUPABASE_URL}/rest/v1/logs"
            payload = {
                "date": date_str,
                "time": time_str,
                "amount_g": float(amount_g),
                "weight_g": float(weight_g),
                "population": int(population),
                "temperature": float(temp),
                "ph": float(ph),
                "water_level": float(lvl),
                "turbidity": float(turb)
            }
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                method="POST"
            )
            with urllib.request.urlopen(req) as response:
                print(f"Logged to Supabase: HTTP {response.status}")
                # Mark as synced in local DB
                c.execute('UPDATE logs SET synced = 1 WHERE id = ?', (log_id,))
                conn.commit()
        except Exception as e:
            print(f"Supabase REST log failed (will sync later): {e}")

    conn.close()

    return {
        "id": log_id, "date": date_str, "len": "40 mm", "feed": f"{amount_g} g", "w": f"{weight_g} g",
        "pop": population, "temp": f"{temp}° C", "ph": ph, "lvl": f"{lvl} cm", "turb": f"{turb} mg/L"
    }

def scheduled_job():
    # Only feed if it's currently one of the scheduled times
    # In a real app we'd trigger the feeder hardware here
    now_hm = datetime.now().strftime("%H:%M")
    calc = calculate_feeding()
    times = get_feeding_times(calc['frequency'])
    if now_hm in times:
        print(f"Time {now_hm} met! Triggering scheduled feed...")
        log_feeding(calc['amount_g'], calc['weight'], calc['population'])

last_sync_time = 0

def sync_to_supabase():
    global last_sync_time
    if time.time() - last_sync_time < 60:
        return # Sync at most once per minute
    
    if not (SUPABASE_URL and SUPABASE_KEY):
        return
        
    last_sync_time = time.time()
    
    try:
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        
        # 1. PUSH: Local -> Supabase
        c.execute('SELECT id, date, time, amount_g, weight_g, population, temperature, ph, water_level, turbidity FROM logs WHERE synced = 0')
        unsynced_rows = c.fetchall()
        
        for row in unsynced_rows:
            log_id = row[0]
            payload = {
                "date": row[1],
                "time": row[2],
                "amount_g": float(row[3]),
                "weight_g": float(row[4]),
                "population": int(row[5]),
                "temperature": float(row[6]),
                "ph": float(row[7]),
                "water_level": float(row[8]),
                "turbidity": float(row[9])
            }
            
            url = f"{SUPABASE_URL}/rest/v1/logs"
            req = urllib.request.Request(
                url, 
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                    "Content-Type": "application/json",
                    "Prefer": "return=minimal"
                },
                method="POST"
            )
            with urllib.request.urlopen(req) as response:
                if response.status in (200, 201, 204):
                    c.execute('UPDATE logs SET synced = 1 WHERE id = ?', (log_id,))
                    conn.commit()
                    print(f"Background sync: Pushed missing log ID {log_id} to Supabase")

        # 2. PULL: Supabase -> Local
        url_pull = f"{SUPABASE_URL}/rest/v1/logs?select=*&order=id.desc&limit=100"
        req_pull = urllib.request.Request(
            url_pull,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        with urllib.request.urlopen(req_pull) as response:
            supa_data = json.loads(response.read().decode())
            
        for s_row in supa_data:
            # Check if this exact date and time exist locally
            c.execute('SELECT id FROM logs WHERE date = ? AND time = ?', (s_row.get('date'), s_row.get('time')))
            if not c.fetchone():
                c.execute('''
                    INSERT INTO logs (date, time, amount_g, weight_g, population, temperature, ph, water_level, turbidity, synced)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 1)
                ''', (
                    s_row.get('date', ''), s_row.get('time', ''), s_row.get('amount_g', 0),
                    s_row.get('weight_g', 0), s_row.get('population', 0), s_row.get('temperature', 0),
                    s_row.get('ph', 0), s_row.get('water_level', 0), s_row.get('turbidity', 0)
                ))
                print(f"Background sync: Pulled missing log from Supabase ({s_row.get('date')} {s_row.get('time')})")

        # 3. PULL DELETIONS: Supabase -> Local
        # Fetch up to 1000 logs from Supabase just to check for deletions
        url_del = f"{SUPABASE_URL}/rest/v1/logs?select=date,time&order=id.desc&limit=1000"
        req_del = urllib.request.Request(
            url_del,
            headers={
                "apikey": SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}"
            }
        )
        with urllib.request.urlopen(req_del) as response:
            supa_all = json.loads(response.read().decode())
            
        supa_set = {f"{r.get('date')}_{r.get('time')}" for r in supa_all}
        
        # Check our local synced logs (top 1000 to match)
        c.execute('SELECT id, date, time FROM logs WHERE synced = 1 ORDER BY id DESC LIMIT 1000')
        local_synced = c.fetchall()
        
        for l_row in local_synced:
            l_id, l_date, l_time = l_row
            key = f"{l_date}_{l_time}"
            if key not in supa_set:
                # If Supabase has >= 1000 rows, there's a chance this row just fell off the pagination end.
                # So only delete if Supabase returned < 1000 rows, OR we know this row is recent.
                if len(supa_all) < 1000 or (l_row != local_synced[-1]):
                    c.execute('DELETE FROM logs WHERE id = ?', (l_id,))
                    print(f"Background sync: Deleted local log ID {l_id} because it was removed from Supabase")

        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Background sync to/from Supabase failed: {e}")

def run_schedule():
    import time
    schedule.every().minute.at(":00").do(scheduled_job)
    while True:
        schedule.run_pending()
        sync_to_supabase()
        time.sleep(1)

# Start background scheduler
scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
scheduler_thread.start()
# Global to track processes and states
water_pump_process = None
feeder_process = None
user_overridden = False
override_time = 0
last_temp_state = "normal"
import time

def start_water_pump():
    global water_pump_process
    import subprocess
    import sys
    script_path = os.path.join(os.path.dirname(__file__), 'AquaMonitor', 'tests', 'water_pump.py')
    if water_pump_process is None or water_pump_process.poll() is not None:
        water_pump_process = subprocess.Popen([sys.executable, script_path, "on"])
        print("Water pump started.", flush=True)
        return True
    return False

def stop_water_pump():
    global water_pump_process
    import subprocess
    import sys
    import os
    script_path = os.path.join(os.path.dirname(__file__), 'AquaMonitor', 'tests', 'water_pump.py')
    
    # First terminate the 'on' loop if it's running
    if water_pump_process is not None and water_pump_process.poll() is None:
        water_pump_process.terminate()
        water_pump_process.wait()
        water_pump_process = None
        
    # Also kill any orphaned processes just to be absolutely sure
    try:
        os.system("pkill -f 'water_pump.py on'")
    except:
        pass
        
    # Then explicitly run the off script to cleanly drive it low before exiting
    subprocess.run([sys.executable, script_path, "off"])
    print("Water pump stopped.", flush=True)

# Ensure pump is off and clean when server starts
try:
    stop_water_pump()
except:
    pass

@app.route('/api/water-filter', methods=['POST'])
def toggle_water_filter():
    global user_overridden, override_time
    req_data = request.get_json(silent=True) or {}
    state = req_data.get('state') # "on" or "off"
    
    user_overridden = True # Mark that user has manually intervened
    override_time = time.time()

    if state == "on":
        if start_water_pump():
            return jsonify({"success": True, "state": "on"})
        return jsonify({"success": True, "message": "Already running", "state": "on"})
            
    elif state == "off":
        stop_water_pump()
        return jsonify({"success": True, "state": "off"})
            
    return jsonify({"success": False, "error": "Invalid state"}), 400

# Global to track feeder subprocess
feeder_process = None

@app.route('/api/feed', methods=['POST'])
def trigger_feed():
    global feeder_process
    
    # Check if feeder is already running
    if feeder_process is not None and feeder_process.poll() is None:
        print("Feeder override is already in progress. Ignoring request.", flush=True)
        return jsonify({"success": False, "error": "Feeder is currently running."}), 409

    # Manual Feed Trigger
    print("Feeder triggered manually!", flush=True)
    
    # Check if weight was passed in request JSON
    req_data = request.get_json(silent=True) or {}
    target_weight = req_data.get('weight')
    
    calc = calculate_feeding()
    # Use target_weight from request if present, else default calculation
    final_weight = target_weight if target_weight else calc['amount_g']
    
    log_data = log_feeding(final_weight, calc['weight'], calc['population'])
    
    # Run feeder2.py with the target weight in a background thread/process
    # Provide the absolute path to feeder2.py
    feeder_script_path = os.path.join(os.path.dirname(__file__), 'AquaMonitor', 'tests', 'feeder2.py')
    if os.path.exists(feeder_script_path):
        import subprocess
        import sys
        # Use sys.executable to ensure it runs in the same virtual environment as server.py
        feeder_process = subprocess.Popen([sys.executable, "AquaMonitor/tests/feeder2.py", str(final_weight)])
        print(f"Started feeder2.py with weight {final_weight}g using {sys.executable}")
    else:
        print(f"Warning: feeder2.py not found at {feeder_script_path}")

    return jsonify({"success": True, "log": log_data})

@app.route('/api/schedule', methods=['GET'])
def get_schedule():
    calc = calculate_feeding()
    times = get_feeding_times(calc['frequency'])
    
    now_date = datetime.now().strftime('%m/%d/%Y')
    schedule_data = []
    for t in times:
        # convert 24h to 12h
        time_obj = datetime.strptime(t, "%H:%M")
        time_12 = time_obj.strftime("%I:%M %p")
        schedule_data.append({
            "date": now_date,
            "time": time_12,
            "feeds": f"{calc['amount_g']} g",
            "weight": f"{calc['weight']} g"
        })
    return jsonify(schedule_data)

@app.route('/api/logs', methods=['GET'])
def get_logs():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, date, time, amount_g, weight_g, population, temperature, ph, water_level, turbidity FROM logs ORDER BY id DESC')
    rows = c.fetchall()
    conn.close()
    
    logs = []
    for r in rows:
        logs.append({
            "id": r[0],
            "date": f"{r[1]} {r[2]}", # Combine date & time since table only has 'Date' column and there's limited space. Or just date. Keep as Dummy data
            "date_val": r[1],
            "time_val": r[2],
            "len": "40 mm", # Mock Length
            "feed": f"{r[3]} g",
            "w": f"{r[4]} g",
            "pop": r[5],
            "temp": f"{r[6]}° C",
            "ph": r[7],
            "lvl": f"{r[8]} cm",
            "turb": f"{r[9]} mg/L"
        })
    return jsonify(logs)

@app.route('/api/logs/<int:log_id>', methods=['DELETE'])
def delete_log(log_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT date, time FROM logs WHERE id = ?', (log_id,))
    row = c.fetchone()
    
    c.execute('DELETE FROM logs WHERE id = ?', (log_id,))
    conn.commit()
    conn.close()
    
    if row and SUPABASE_URL and SUPABASE_KEY:
        date_str, time_str = row
        try:
            # Delete by matching date and time
            url = f"{SUPABASE_URL}/rest/v1/logs?date=eq.{urllib.parse.quote(date_str)}&time=eq.{urllib.parse.quote(time_str)}"
            req = urllib.request.Request(
                url, 
                headers={
                    "apikey": SUPABASE_KEY,
                    "Authorization": f"Bearer {SUPABASE_KEY}",
                },
                method="DELETE"
            )
            with urllib.request.urlopen(req) as response:
                print(f"Deleted from Supabase: HTTP {response.status}")
        except Exception as e:
            print(f"Supabase delete failed: {e}")
            
    return jsonify({"success": True})

@app.route('/api/settings', methods=['POST'])
def update_settings():
    data = request.json
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        UPDATE settings SET population=?, length=?, width=?, depth=?, weight=?, mock_weight=? WHERE id=1
    ''', (data.get('population', 15), data.get('length', 172), data.get('width', 194), data.get('depth', 75), data.get('weight', 250), data.get('mock_weight', 20)))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/settings', methods=['GET'])
def fetch_settings():
    return jsonify(get_settings())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)

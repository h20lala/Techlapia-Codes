import time
import datetime
import os
import logging
from tabulate import tabulate
import pandas as pd

import config
from sensors.ads1115 import ADCSensor
from sensors.ds18b20 import TempSensor
from sensors.hx711_scale import ScaleSensor
from sensors.ph_sensor import PHSensor
from sensors.turbidity import TurbiditySensor
from sensors.water_level import WaterLevelSensor

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    print("AquaMonitor System Starting...")
    
    # 1. Initialize Sensors
    # Shared ADC
    adc_driver = ADCSensor()
    adc_driver.initialize()
    
    # Temperature
    temp_sensor = TempSensor()
    
    # Scale
    scale_sensor = ScaleSensor(config.PIN_HX711_DT, config.PIN_HX711_SCK, 
                               config.SCALE_REFERENCE_UNIT, config.SCALE_OFFSET)
    
    # pH
    ph_sensor = PHSensor(config.CHANNEL_PH, config.PH_SLOPE, config.PH_INTERCEPT)
    
    # Turbidity
    turb_sensor = TurbiditySensor(config.CHANNEL_TURBIDITY)
    
    # Water Level
    level_sensor = WaterLevelSensor(config.PIN_FLOAT_SWITCH)
    
    # 2. Setup Data Logging
    if not os.path.exists(config.DATA_DIR):
        os.makedirs(config.DATA_DIR)
        
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = os.path.join(config.DATA_DIR, f"data_{timestamp_str}.csv")
    
    # Initialize CSV with headers
    df = pd.DataFrame(columns=["Timestamp", "Temperature_C", "pH", "Turbidity_NTU", "Turbidity_V", "Weight", "WaterLevel"])
    df.to_csv(csv_filename, index=False)
    print(f"Logging data to: {csv_filename}")
    
    print("Press Ctrl+C to stop.")
    time.sleep(2)

    try:
        while True:
            cycle_start = time.time()
            
            # --- READ SENSORS ---
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Temp
            temp_c = temp_sensor.read_temperature()
            
            # pH
            ph_val, ph_volt = ph_sensor.read_ph()
            
            # Turbidity
            turb_ntu, turb_volt = turb_sensor.read_turbidity()
            
            # Weight
            weight = scale_sensor.read_weight()
            
            # Water Level
            level_status = level_sensor.get_status()
            
            # --- DISPLAY ---
            table_data = [
                ["Time", current_time],
                ["Temperature", f"{temp_c:.2f} C"],
                ["pH", f"{ph_val:.2f} (V: {ph_volt:.2f})"],
                ["Turbidity", f"{turb_ntu:.2f} NTU (V: {turb_volt:.2f})"],
                ["Weight", f"{weight:.2f}"],
                ["Water Level", level_status]
            ]
            
            # Clear screen (optional, maybe just print block)
            # os.system('clear') 
            print("\n" + "="*40)
            print(tabulate(table_data, headers=["Metric", "Value"], tablefmt="pretty"))
            
            # --- LOGGING ---
            new_row = {
                "Timestamp": current_time,
                "Temperature_C": temp_c,
                "pH": ph_val,
                "Turbidity_NTU": turb_ntu,
                "Turbidity_V": turb_volt,
                "Weight": weight,
                "WaterLevel": level_status
            }
            
            # Append using pandas is slow for loops, better to use open(file, 'a') for realtime
            # but for thesis simplicity pandas is okay, or csv writer.
            # Let's use csv writer for performance and safety.
            with open(csv_filename, 'a') as f:
                # Simple CSV formatting
                line = f"{current_time},{temp_c},{ph_val},{turb_ntu},{turb_volt},{weight},{level_status}\n"
                f.write(line)
            
            # Wait
            elapsed = time.time() - cycle_start
            sleep_time = max(0, config.LOG_INTERVAL_SECONDS - elapsed)
            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nStopping AquaMonitor...")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()

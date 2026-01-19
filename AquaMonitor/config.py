# Configuration for AquaMonitor System

# --- GPIO Settings (BCM Numbering) ---
# DS18B20 is typically 1-Wire (GPIO 4 by default on Pi, but can be configured)
# Float Switch
PIN_FLOAT_SWITCH = 17 

# HX711 Load Cell
PIN_HX711_DT = 5
PIN_HX711_SCK = 6

# --- I2C Addresses ---
# ADS1115 ADCs
I2C_ADDR_ADS1115 = 0x48

# --- Analog Config (ADS1115) ---
# Channel mapping
CHANNEL_PH = 0        # A0
CHANNEL_TURBIDITY = 1 # A1

# --- Calibration Constants ---

# pH Sensor
# Linear formula: y = mx + c  (y: pH, x: Voltage)
# Default values for generic probe, MUST BE CALIBRATED
PH_SLOPE = -5.70 
PH_INTERCEPT = 21.34

# Load Cell
# Reference unit obtained during calibration
SCALE_REFERENCE_UNIT = 3580.2074
SCALE_OFFSET = 4875877.4

# Turbidity
# Polynomial or linear relation between Voltage and NTU
# This is highly sensor-specific.
# Simplified model: NTU = -1120.4 * V^2 + 5742.3 * V - 4353.8 (Example)
# For now, we will log raw voltage and a simple linear map
TURBIDITY_MAX_VOLTAGE = 4.2 # Pure water (approx)
TURBIDITY_THRESHOLD = 2.5   # Dirty water

# --- System Settings ---
LOG_INTERVAL_SECONDS = 1
DATA_DIR = "data"

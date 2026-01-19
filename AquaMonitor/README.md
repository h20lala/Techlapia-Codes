# AquaMonitor - Raspberry Pi 5 Aquaculture System

A modular, Python-based aquaculture monitoring system designed for the Raspberry Pi 5.
This system monitors Weight, Temperature, pH, Turbidity, and Water Level, logging data to CSV in real-time.

## Features
- **Real-time Monitoring**: Display sensor data in the terminal.
- **Data Logging**: Auto-saves data to `data/data_YYYYMMDD_HHMMSS.csv`.
- **Modular Design**: Independent drivers for each sensor.
- **Pi 5 Compatible**: Uses `lgpio` / `gpiozero` for modern GPIO handling.

## Hardware Requirements
- Raspberry Pi 5 (64-bit OS)
- **ADC**: ADS1115 (16-bit)
- **Sensors**:
  - Load Cell (Verified with HX711)
  - DS18B20 Temperature Probe
  - PH-4502C pH Sensor Module
  - Analog Turbidity Sensor (e.g., DFRobot Gravity)
  - Float Switch (Digital)

## Wiring Guide

> [!WARNING]
> **Voltage Levels**: The Raspberry Pi GPIO is **3.3V logic**. The ADS1115 I2C lines must be 3.3V. If you power the ADS1115 with 5V, you MUST use an I2C Level Shifter. Alternatively, power the ADS1115 with 3.3V. Ensure analog inputs do not exceed the ADS1115 power supply voltage.

| Sensor | Pin/Label | Connect To (Pi / ADS1115) | Note |
| :--- | :--- | :--- | :--- |
| **ADS1115** | VDD | 3.3V | Power |
| | GND | GND | Ground |
| | SCL | GPIO 3 (SCL) | I2C Clock |
| | SDA | GPIO 2 (SDA) | I2C Data |
| **pH Sensor** | Signal (Po) | ADS1115 A0 | Analog In |
| **Turbidity** | Signal | ADS1115 A1 | Analog In |
| **DS18B20** | Data | GPIO 4 | 1-Wire Default |
| **HX711** | DT | GPIO 5 | Configurable |
| | SCK | GPIO 6 | Configurable |
| **Float Switch** | Wire 1 | GPIO 17 | |
| | Wire 2 | GND | |

## Installation

1.  **System Setup**
    Ensure I2C and 1-Wire are enabled in `sudo raspi-config`.

2.  **Create Virtual Environment** (Required on Pi 5)
    ```bash
    cd "Techlapia Codes/AquaMonitor"
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Calibration (Important First Step)**
    Run the scripts in `calibration/` to get accurate constants.
    
    ### HX711 Load Cell Calibration
    1.  **Wiring Check**: Ensure DT is on **GPIO 5** and SCK is on **GPIO 6**.
    2.  **Run Script**: 
        ```bash
        python calibration/calibrate_scale.py
        ```
    3.  **Tare**: Remove all items from the scale and press Enter. The script will calculate the zero-offset.
    4.  **Weigh**: Place a object of **known weight** on the scale (e.g., a 1kg weight, or a water bottle usually ~500g).
    5.  **Input**: Enter the weight value when prompted (e.g., `1000` for grams or `1.0` for kg).
    6.  **Save**: The script will print `REFERENCE_UNIT` and `OFFSET`. Copy these values into `config.py` to replace the defaults.

    ### pH Calibration
    1.  run `python calibration/calibrate_ph.py`
    2.  Follow the prompts using two buffer solutions (usually pH 4.0 and 7.0).
    3.  Update `PH_SLOPE` and `PH_INTERCEPT` in `config.py`.

    ### Turbidity Calibration
    1.  run `python calibration/calibrate_turbidity.py`
    2.  Record voltage for Clear Water vs Dirty Water.
    3.  Update logic in `sensors/turbidity.py` if needed (config only stores thresholds currently).

2.  **Run System**
    ```bash
    python main.py
    ```
    To stop, press `Ctrl+C`.

3.  **Data**
    Logs are saved in the `data/` folder.

## Project Structure
- `main.py`: Main loop.
- `config.py`: Pin definitions and calibration settings.
- `sensors/`: Driver modules.
- `calibration/`: Scripts for sensor setup.

from gpiozero import Button
import logging

class WaterLevelSensor:
    def __init__(self, pin):
        """
        Initialize the float switch. 
        Treating it as a Button (open/closed).
        Make sure to configure internal pull-up/down correctly or use external resistor.
        Common float switches are simple reed switches.
        """
        self.pin = pin
        self.sensor = None
        self.initialize()

    def initialize(self):
        try:
            # pull_up=True implies connection to Ground when closed.
            # Adjust based on wiring. Assuming switch connects Pin to GND.
            self.sensor = Button(self.pin, pull_up=True) 
            logging.info(f"Water Level Sensor initialized on GPIO {self.pin}")
        except Exception as e:
            logging.error(f"Failed to initialize Water Level Sensor on pin {self.pin}: {e}")
            self.sensor = None

    def is_water_low(self):
        """
        Returns True if water is LOW (switch activated/open depending on float type).
        Assuming:
        - Float down (Low water) -> Switch Open -> Input High (Pull-up) -> is_pressed=False
        - Float up (High water) -> Switch Closed -> Input Low -> is_pressed=True
        
        Logic needs to be verified with specific sensor hardware.
        Let's assume 'is_pressed' corresponds to enough water.
        """
        if self.sensor is None:
            return True # Assume error/low safety

        # If using Button with pull_up=True:
        # Pressed (Closed) = Low Voltage = True
        # Released (Open) = High Voltage = False
        
        # Usually: Float down = Open circuit. Float up = Closed.
        # So is_pressed (Closed) means Water is High.
        # Not is_pressed (Open) means Water is Low.
        return not self.sensor.is_pressed
    
    def get_status(self):
        if self.is_water_low():
            return "LOW"
        else:
            return "OK"

from flask import Flask, render_template, request, flash, session
from src.services.ArdLedWrapper import ArdLedWrapper
import subprocess
from markupsafe import escape
import sqlite3
import requests
import json
import time

app = Flask(__name__)

ard_wrapper = ArdLedWrapper()

class FlaskLED():
    def __init__(self):
        self.configs = {
            "state": "0",
            "color": [0,0,0],
            "brightness": 0
        }
        self.sessions = 0
        self.valid_states = ["0", "1"]
        self.valid_color_brightness_range = {"min": 0, "max": 255}
        self.ard_file_path = "src/services/led_config.json"

    # def get_chcv(self):
    #     return self.CHSV
    
    # def set_chsv(
    #     self, 
    #     color: list = None,
    #     sv: int = None
    # ) -> bool:
    #     # For all None parameters, set them to the class attribute value
    #     if color is None:
    #         c = self.CHSV["C"]
    #     if h is None:
    #         h = self.CHSV["H"]
    #     if sv is None:
    #         sv = self.CHSV["SV"]
    #     # Check that all passed values are ints and within range thresholds
    #     if isinstance(c, int) and  isinstance(c, int) and isinstance(c, int) and (c < 256 and c > -1) and (h < 256 and h > -1) and (sv < 256 and sv > -1):
    #         self.CHSV["C"] = c
    #         self.CHSV["H"] = h
    #         self.CHSV["SV"] = sv
    #         return True
    #     else:
    #         return False

flask_led = FlaskLED()

# Main route
@app.route('/flask_led', methods=('GET', 'POST'))
def hello_world():
    while not ard_wrapper.connected:
        ard_wrapper.connect_to_ard()
    return render_template('index.html')

# Update whatever configs are passed
@app.route('/update_led_config', methods=['POST'])
def update_led_config():
    with open(flask_led.ard_file_path, "r+") as f:
        data = json.load(f)
        # Loop through arguments
        for arg in request.args:
            # If the arg is not in the configs, return
            if arg not in flask_led.configs:
                print("Passed invalid query argument, Error 404 lol")
                return "BAD ARG"
            # Check each argument
            # TODO: Incorporate type checks here... What if we get somthing we are not expecting?
            if arg == "state":
                if request.args[arg] not in flask_led.valid_states:
                    print("Passed invalid state, Error 404 lol")
                    return "BAD"
                else:
                    data["state"] = int(request.args[arg])
            if arg == "color":
                val = int(request.args[arg])
                if val < flask_led.valid_color_brightness_range["min"] or val > flask_led.valid_color_brightness_range["max"]:
                    print("Passed invalid color value, Error 404 lol")
                    return "BAD"
                else:
                    data["color"] = val
            if arg == "brightness":
                val = int(request.args[arg])
                if val < flask_led.valid_color_brightness_range["min"] or val > flask_led.valid_color_brightness_range["max"]:
                    print("Passed invalid brightness value, Error 404 lol")
                    return "BAD"
                else:
                    data["brightness"] = val
        # Write new data
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    ard_wrapper.send_message(json.dumps(data)+"**")
    msg = ard_wrapper.read_message(128)
    return msg.decode("utf-8").replace("\n","").replace("\r","")

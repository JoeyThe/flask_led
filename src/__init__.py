from flask import Flask, render_template, request, flash, session
from src.services.ArdLedWrapper import ArdLedWrapper
import subprocess
from markupsafe import escape
import sqlite3
import requests
import json
import time
import os

app = Flask(__name__)

class FlaskLED():
    def __init__(self):
        self.led_config_file_path = "src/services/led_config.json"
        self.flask_config_file_path = "src/services/flask_config.json"

        with open(self.led_config_file_path, "r") as f:
            data = json.load(f)
        self.values = {
            "state": data["state"],
            "color": data["color"],
            "brightness": data["brightness"]
        }
        with open(self.flask_config_file_path, "r") as f:
            self.flask_data = json.load(f)

        self.sessions = 0
        self.valid_states = ["0", "1"]
        # self.valid_brightness_range = {"min": 0, "max": 255}
        # self.valid_color_range = {"min": 0, "max": 255}

    def update_values(self):
        with open(self.led_config_file_path, "r") as f:
            data = json.load(f)
        self.values = {
            "state": data["state"],
            "color": data["color"],
            "brightness": data["brightness"]
        }

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

ard_wrapper = ArdLedWrapper()
flask_led = FlaskLED()

# Main route
@app.route('/flask_led', methods=('GET', 'POST'))
def hello_world():
    while not ard_wrapper.connected:
        print("ARD created", flush=True)
        ard_wrapper.connect_to_ard()
    flask_led.update_values()
    return render_template('index.html', load_state=["Off" if flask_led.values["state"] == 1 else "On"][0],
                           load_color=flask_led.values["color"],
                           load_brightness=flask_led.values["brightness"],
                           min_color=flask_led.flask_data["valid_color_range"]["min"],
                           max_color=flask_led.flask_data["valid_color_range"]["max"],
                           min_brightness=flask_led.flask_data["valid_brightness_range"]["min"],
                           max_brightness=flask_led.flask_data["valid_brightness_range"]["max"])

# Update whatever configs are passed
@app.route('/update_led_config', methods=['POST'])
def update_led_config():
    with open(flask_led.led_config_file_path, "r+") as f:
        data = json.load(f)
        # Loop through arguments
        for arg in request.args:
            # If the arg is not in the configs, return
            if arg not in flask_led.values:
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
                if val < flask_led.flask_data["valid_brightness_range"]["min"] or val > flask_led.flask_data["valid_brightness_range"]["max"]:
                    print("Passed invalid color value, Error 404 lol")
                    return "BAD"
                else:
                    data["color"] = val
            if arg == "brightness":
                val = int(request.args[arg])
                if val < flask_led.flask_data["valid_color_range"]["min"] or val > flask_led.flask_data["valid_color_range"]["max"]:
                    print("Passed invalid brightness value, Error 404 lol")
                    return "BAD"
                else:
                    data["brightness"] = val
        # Write new data
        f.seek(0)
        json.dump(data, f)
        f.truncate()
    try:
        data_str = json.dumps(data)
        out_msg = data_str+"{:02x}".format(len(data_str)+4)+"**"
        ard_wrapper.send_message(out_msg)
        print(out_msg, flush=True)
        time.sleep(1.5)
        in_msg = ard_wrapper.read_message(ard_wrapper.BUFF_SIZE)
        print(in_msg, flush=True)
    except Exception:
        print("Error reading message, in_msg=BAD", flush=True)
        return "BAD"
    if in_msg is not None:
        return in_msg.decode("utf-8").replace("\n","").replace("\r","")
    else:
        print("Error reading message, in_msg=BAD", flush=True)
        return "BAD"

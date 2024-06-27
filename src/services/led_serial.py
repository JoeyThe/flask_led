import serial
import subprocess
import time
import traceback
import json
import os

SERIALPORT = "/dev/ttyACM0"
BAUDRATE = 9600

ser = serial.Serial(SERIALPORT, BAUDRATE, timeout=1)

try:
    ser.open()
except:
    print("Port already open")
    ser.close()
    ser.open()

def get_led_option_text():
    # Run a subprocess to get the contents of the led_option.txt file as a string
    try:
        cat_result = subprocess.run(["cat", "led_config.json"], stdout=subprocess.PIPE)
        led_option_str = cat_result.stdout.decode().rstrip()
    except:
        print("cat subprocess failed. Exception\n")
        traceback.print_exc()
        return None
    
    return json.loads(led_option_str)

if __name__ == "__main__":
    # Get inital file values
    time.sleep(1)
    old_data = get_led_option_text()
    if old_data is None:
        print("Could not read file on initialization. Exiting...")
        os._exit()

    # Init
    init = False
    while not init:
        ser.write(bytes("init**", "utf-8"))
        time.sleep(1)
        init_resp = ser.read(128)
        print(init_resp)
        if init_resp == bytes("INITIATED", "utf-8"):
            init = True
            print("Serial connection initiated")

    # LED loop
    while True:
        # Wait a second whippersnapper
        time.sleep(1)
        
        # Read led_option 
        data = get_led_option_text()
        if data is None:
            continue

        # Determine what is different (if anything)
        is_diff = False
        for field in data:
            if data[field] != old_data[field]:
                is_diff = True
                print(f"{field} is being updated to {data[field]} (was {old_data[field]})")
                old_data[field] = data[field]

        if is_diff:
            # Attempt to write bytes to arduino
            data = json.dumps(data)+"**"
            try:
                data_bytes = data.encode("utf-8")
                ser.write(data_bytes)
                print("Bytes written")
            except Exception:
                print("Unable to write bytes. Exception:\n")
                traceback.print_exc()
                continue
            # Wait a second whippersnapper
            time.sleep(1)
            # Read response from arduino
            try:
                resp = ser.read(128)
                print("Bytes read")
                print(f"Read data: {resp}")
            except Exception:
                print("Unable to read bytes. Exception:\n")
                traceback.print_exc()

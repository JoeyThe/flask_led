import serial
import subprocess
import time
import traceback
import json

SERIALPORT = "/dev/ttyACM0"
BAUDRATE = 9600

# ser = serial.Serial(SERIALPORT, BAUDRATE, timeout=1)
#time.sleep(10)
old_data = {"state": "off", "color": [0, 0, 0], "sv": 0}

# ser.write(bytes("init", "utf-8"))
# ser.read(128)

# try:
#     ser.open()
# except:
#     print("Port already open")
#     ser.close()
#     ser.open()

while True:
    # Wait a second whippersnapper
    time.sleep(1)

    # Run a subprocess to get the contents of the led_option.txt file as a string
    try:
        cat_result = subprocess.run(["cat", "led_option.json"], stdout=subprocess.PIPE)
        # led_option = subprocess.check_output(["cat", "led_option.txt"])
        led_option_str = cat_result.stdout.decode().rstrip()
    except:
        print("cat subprocess failed. Exception\n")
        traceback.print_exc()
        continue
    
    data = json.loads(led_option_str)

    # Determine what is different (if anything)
    for field in data:
        if data[field] != old_data[field]:
            print(f"{field} is being updated to {data[field]} (was {old_data[field]})")
            old_data[field] = data[field]

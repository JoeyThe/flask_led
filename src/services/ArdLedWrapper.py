import serial
import subprocess
import time
import traceback
import json
import os

class ArdLedWrapper:
    def __init__(self):
        self.SERIALPORT = "/flask_led/tty"
        # self.SERIALPORT = "/dev/ttyACM0"
        self.BAUDRATE = 9600
        self.BUFF_SIZE = 128
        self.connected = False
        self.ser = serial.Serial(self.SERIALPORT, self.BAUDRATE, timeout=2)

        try:
            self.ser.open()
        except Exception:
            self.ser.close()
            self.ser.open()

    def connect_to_ard(self) -> bool:
        self.ser.write(bytes("init**", "utf-8"))
        init_resp = self.ser.read(self.BUFF_SIZE)
        if init_resp == bytes("INITIATED", "utf-8"):
            self.connected = True
        return self.connected

    def send_message(self, msg: str) -> bool:
        try:
            self.ser.write(msg.encode("utf-8"))
            return True
        except Exception:
            print("Unable to write bytes. Exception:\n")
            traceback.print_exc()
            return None

    def read_message(self, size: int) -> bytes:
        try:
            msg = self.ser.read(size)
            return msg
        except Exception:
            print("Unable to write bytes. Exception:\n")
            traceback.print_exc()
            return None

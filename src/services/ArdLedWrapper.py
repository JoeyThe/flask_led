import serial
import subprocess
import time
import traceback
import json
import os

class ArdLedWrapper:
    def __init__(self):
        self.SERIALPORT = "/dev/ttyACM0"
        self.BAUDRATE = 9600
        self.connected = False
        self.ser = serial.Serial(self.SERIALPORT, self.BAUDRATE, timeout=0.1)

        try:
            self.ser.open()
        except:
            self.ser.close()
            self.ser.open()

    def connect_to_ard(self) -> bool:
        self.ser.write(bytes("init**", "utf-8"))
        init_resp = self.ser.read(128)
        if init_resp == bytes("INITIATED", "utf-8"):
            self.connected = True
        return self.connected

    def send_message(self, msg: str) -> bool:
        try:
            self.ser.write(msg.encode("utf-8"))
            return True
        except:
            print("Unable to write bytes. Exception:\n")
            traceback.print_exc()
            return False

    def read_message(self, size: int) -> bytes:
        try:
            msg = self.ser.read(size)
            return msg
        except:
            print("Unable to write bytes. Exception:\n")
            traceback.print_exc()
            return None

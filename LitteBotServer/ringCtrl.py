#!/usr/bin/env python3
# from pyosc import Server
from sys import platform as _platform
from threading import Thread
import subprocess

# UNUSED see LitteBotSound

class Loop(Thread):
    def __init__(self, file):
        Thread.__init__(self)
        self.file = file

    def stop(self):
        self.proc.terminate()

    def run(self):
        if _platform == "darwin":
            self.proc = subprocess.Popen(["ffplay -nodisp -loop 0 -autoexit -loglevel quiet "+self.file], shell=True)
        elif _platform == "win32" or _platform == "win64":
            self.proc = subprocess.Popen(["ffplay.exe -nodisp -loop 0 -autoexit -loglevel quiet "+self.file], shell=True)

class PhoneCtrl():
    def __init__(self):
        # self.osc_server = Server('127.0.0.1', 14012, self.oscIn)
        self.loop = None

    def ring(self):
        if self.loop :
            self.loop.stop()
        self.loop = Loop("../sounds/phoneRing.wav")
        self.loop.start()

    def hang(self):
        if self.loop :
            self.loop.stop()
        self.loop = Loop("../sounds/phoneHang.wav")
        self.loop.start()

    def stop(self):
        if self.loop :
            self.loop.stop()
            self.loop = None

    def oscIn(self, address, *args):
        # print("OSCin", address, args)
        if address == "/stop" :
            # print("STOP")
            if self.loop :
                self.loop.stop()
                self.loop = None
        elif address == "/start" :
            # print("PLAY")
            if self.loop :
                self.loop.stop()
            self.loop = Loop("./391870_phone.wav")
            self.loop.start()

if __name__ == '__main__':
    PhoneCtrl()

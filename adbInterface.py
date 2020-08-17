#!/usr/bin/python

import subprocess
import os
import sys
import time
import random
from PIL import Image
from PIL import ImageFile
import cv2.cv2 as cv2

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class adbInterface:
    adbpath = '.\\platform-tools\\adb'
    serial = ""

    def __init__(self):
        # print("Started ADB Interface Controller")
        # print("---Finding devices serial---")
        self.serial = self.adbdevices()
        print("---Serial found " + self.serial + "---")
        return
    def adbshell(self, command):
        
        # print("ADB Shell Command")
        args = [self.adbpath]
        if self.serial is not None:
            args.append('-s')
            args.append(self.serial)
        args.append('shell')
        args.append(command)
        # print(args)
        return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)

    def adbpull(self, command):
        args = [self.adbpath]
        args.append('pull')
        args.append(command)
        # print(args)
        return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)

    def adbdevices(self):
        # create a tuple with the arguments for the command
        args = [self.adbpath]
        args.append('devices')
        # run command to shell (This is not hazardos while shell=True because
        # the args input is not dependant in user input)
        child = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)
        # split the bytes string where I can get the serial of the device
        bSerial = child.stdout.read().split(b'\n')[1].split(b'\t')[0]
        # decode the bytes into string
        return bSerial.decode()

    def touchscreen_devices(self):
        child = self.adbshell('getevent -il')
        bTouchdev = child.stdout.read().split(b'add device ')
        bTouchdev = list(filter(lambda x: x.find(b'ABS_MT_POSITION_X') > -1, bTouchdev))[0]
        return bTouchdev.decode()

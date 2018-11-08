#!/usr/bin/python

import subprocess
import os
import sys
import time
import random
from PIL import Image
from PIL import ImageFile
from pytesser import *
import cv2.cv2 as cv2

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

class adbInterface:
    adbpath = '..\\platform-tools\\.\\adb'
    serial = ""

    def __init__(self):
        return 
    def adbshell(self, command):
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
        print(args)
        bSerial = child.stdout.read().split(b'\n')[1].split(b'\t')[0]
        # decode the bytes into string
        return bSerial.decode()

    def touchscreen_devices(self):
        child = self.adbshell('getevent -il')
        bTouchdev = child.stdout.read().split(b'add device ')
        bTouchdev = list(filter(lambda x: x.find(b'ABS_MT_POSITION_X') > -1, bTouchdev))[0]
        return bTouchdev.decode()

    # def screenCapture(self):
    #     # perform a search in the sdcard of the device for the SummonerBot
    #     # folder. if we found it, we delete the file inside and capture a 
    #     # new file.
    #     child = self.adbshell('ls sdcard')
    #     bFiles = child.stdout.read().split(b'\n')
    #     bFiles = list(filter(lambda x: x.find(b'SummonerBot\r') > -1, bFiles))
    #     if  len(bFiles) == 0:
    #         print("-----------------creating new folder-----------------")
    #         self.adbshell('mkdir -m 777 /sdcard/SummonerBot')
    #     self.adbshell('screencap -p /sdcard/SummonerBot/capcha.jpg')
    #     return ""
        
    # def getScreenCapture(self):
    #     self.screenCapture()
    #     # Pull image from the phone
    #     self.adbpull("/sdcard/SummonerBot/capcha.jpg")
    #     time.sleep(1)
    #     return "capcha"

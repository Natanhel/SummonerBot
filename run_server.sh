#!/bin/bash
adb.exe tcpip 5555
adb.exe shell "ifconfig | grep -A 1 wlan0 | tail -n 1 | cut -f2 -d: | cut -f1 -d' '" | adb.exe connect
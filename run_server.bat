adb.exe tcpip 5555
adb.exe shell "ifconfig | grep -A 1 wlan0 | tail -n 1 | cut -f2 -d: | cut -f1 -d' '" > tmpFile.txt
set /p my_ip=<tmpFile.txt
adb.exe connect %my_ip%
del tmpFile.txt
pause
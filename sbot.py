#!/usr/bin/python

import subprocess
import os
import sys
import time
import random
# from PIL import Image
# from PIL import ImageFile
from pytesser import *
# import cv2.cv2 as cv2
from adbInterface import adbInterface as adb
import sys, getopt

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
adbpath = '..\\platform-tools\\.\\adb'
serial = ""
ImageFile.LOAD_TRUNCATED_IMAGES = True
sellRunes = True
soldRunes = 0
keptRunes = 0
notRuneCnt = 0
revivedCnt = 0
totalRefills = 0
legend = 0
hero = 0
rare = 0
adb = adb()

# This function is a generic implementation for tapping the screen via ADB
# input:    x,y - coordinations for the click on the screen
# output:   a tap on ADB
def tap(x, y):
    command = "input tap " + str(x) + " " + str(y)
    command = str.encode(command)
    adb.adbshell(command.decode('utf-8'))

# This function captures the screen as it is
# input:    none
# output:   blank string
def screenCapture():
    # perform a search in the sdcard of the device for the SummonerBot
    # folder. if we found it, we delete the file inside and capture a
    # new file.
    child = adb.adbshell('ls sdcard')
    bFiles = child.stdout.read().split(b'\n')
    bFiles = list(filter(lambda x: x.find(b'SummonerBot\r') > -1, bFiles))
    if  len(bFiles) == 0:
        print("-----------------creating new folder-----------------")
        adb.adbshell('mkdir -m 777 /sdcard/SummonerBot')
    adb.adbshell('screencap -p /sdcard/SummonerBot/capcha.jpg')
    return ""

# This function clear command line text
# input:    none
# output:   none
def clearConsole():
    os.system('cls')

# This function wait a time epoch given while printing the countdown on stdio
# input:    timeEpoch - time lapse for the countdown
# output:   stdio output
def sleepPrinter(timeEpoch):
    # print("sleeping for: " + str(timeEpoch) + " seconds")
    sleepCountdown(timeEpoch)

# This function wait a time epoch given
# input:    timeEpoch - time lapse for the countdown
# output:   stdio output
def sleepCountdown(timeEpoch):
    last_sec = 0
    for i in range(0,int(timeEpoch)):
        sys.stdout.write('\r' + str(int(timeEpoch)-i)+' ')
        sys.stdout.flush()
        time.sleep(1)
        last_sec = i
    if timeEpoch-float(last_sec+1) > 0:
        time.sleep(timeEpoch-float(last_sec+1))
    sys.stdout.write('\r')
    sys.stdout.flush()
        # print("")
        # print("waiting reminder: " + str(timeEpoch-float(last_sec+1)))

# This function converts TIF files to text tuples
# input:    fileName - file name
# output:   text - tuple with text read from photo
def tif2text(fileName):
    image_file = fileName
    text = ""
    try:
        im = Image.open(image_file + '.tif')
        text = image_to_string(im)
        text = image_file_to_string(image_file + '.tif')
        text = image_file_to_string(image_file + '.tif', graceful_errors=True)
    except IOError:
        print("Error converting tif to text")
    except errors.Tesser_General_Exception:
        print("Error converting tif to text in Tesseract")

    return text

# This function converts TIF files to JPG files
# input:    fileName - file name
# output:   photo with JPG extension
def convTIF2PNG(fileName):
    image_file = Image.open(fileName + '.tif').convert('L')
    image_file.save(fileName + '.jpg')

# This function converts JPG files to TIF files
# input:    fileName - file name
# output:   photo with TIF extension
def convPNG2TIF(fileName):
    try:
        image_file = Image.open(fileName + '.jpg').convert('L')
        image_file.save(fileName + '.tif')
    except IOError:
        print("Error saving from jpg to tif")

# This function checks if the rune is a 6* rune
# input:    fileName - file name
# output:   res - a flag with the answer
def checkSixStar(fileName):
    res = False
    im_gray = cv2.imread(fileName+".jpg", cv2.IMREAD_GRAYSCALE)
    thresh = 127
    im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    try:
        if im_bw is not None:
            res = im_bw[363][690] == im_bw[363][675]
            print("Found it to be a 6*? " + str(res))
    except IOError:
        print("No picture found")
    return res

# This function captures the photo on the screen. preparations for OCR.
# input:    none
# output:   file in jpg format
def getScreenCapture():
    screenCapture()
    # Pull image from the phone
    adb.adbpull("/sdcard/SummonerBot/capcha.jpg")
    time.sleep(1)
    return "capcha"

# This function crops a picture from lower leftmost point x,y to h,w point
# input:    x           - place of x axis
#           y           - place of y axis
#           h           - hieght of x
#           w           - hieght of y
#           fileName    - file name
# output:   cropped image in jpg format in defualt folder
def crop(x,y,h,w,fileName):
    try:
        img = cv2.imread(fileName + '.jpg')
        if img is not None:
            crop_img = img[y:y+h, x:x+w]
            cv2.imwrite(fileName + "_c.jpg", crop_img)
    except IOError:
        print("Could not open file " + fileName)
    return fileName + "_c"

# This function crops the capcha.tif file to [0,0] for reset purposes
# input:    none
# output:   prints to stdio
#           new capcha file reset to [0,0]
def crop2Default():
    try:
        img = cv2.imread('capcha_c.tif')
        if img is not None:
            crop_img = img[0, 0]
            cv2.imwrite("capcha_c.tif", crop_img)
    except IOError:
        print("Could not open file capcha_c.tif")

    try:
        img = cv2.imread('capcha_c.jpg')
        if img is not None:
            crop_img = img[0, 0]
            cv2.imwrite("capcha_c.jpg", crop_img)
    except IOError:
        print("Could not open file capcha_c.jpg")

# This function handles the OCR gathering
# input:    none
# output:   ADB commands
#           informative return values:
#               - "refill"                  - refill command
#               - "revive"                  - revive command
#               - "correct"                 - CAPCHA command
#               - "dc"                      - disconnected before match
#               - "dc_before_run"           - disconnected after match
#               - "reward"                  - reward command
#               - "performed OCR reading"   - nothing found in OCR
def performOCR():
    global totalRefills
    fileN = crop(870,370,50,180,getScreenCapture())
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    # The reward lexema can be found in many places as OCR algorithm isn't exactly precise
    # Therefore, added a few
    rewardList = [  "Reward","Rewand","Rewamdi","Rewamd", "Rgewand", "Rgwand"
                    "Reiwamdi","iiiiii","Prepare","LEVEL", "Rgewamd", "mamd", "wand"
                    "rune","magic"]

    for text in fullText:
        for lexema in rewardList:
            if text.find(lexema) != -1:
                return "reward"
        if text.find("enough") != -1:
            totalRefills += 1
            return "refill"
        if text.find("Revive") != -1:
            return "revive"
        if text.find("amplify") != -1:
            return "grindstone"        
        if text.find("change") != -1:
            return "grindstone"
        if text.find("correct") != -1:
            return "correct"
        if text.find("count as a loss") != -1:
            return "dc"
        if text.find("connection") != -1:
            return "dc_before_run"
        if text.find("Damage") != -1:
            return "beasts_win"

    print(fullText)

    return "performed OCR reading "

# This function handles the state where there's no energy left
# input:    none
# output:   ADB commands
def refillEnergy():
    print("Clicked Refill")
    tap(random.randint(690,700),random.randint(600,700))
    sleepPrinter(2)

    print("Clicked recharge energy")
    tap(random.randint(694,696),random.randint(400,500))
    sleepPrinter(3)

    print("Clicked confirm buy")
    tap(random.randint(690,700),random.randint(600,700))
    sleepPrinter(4)

    print("Clicked purchase successful")
    tap(random.randint(940,990),random.randint(600,650))
    sleepPrinter(3)

    print("Clicked close shop")
    tap(random.randint(850,1050),random.randint(880,980))
    sleepPrinter(3)

def exitRefill():
    print("Clicked Close Purchase")
    tap(random.randint(1760,1850),random.randint(75,140))

def readCapchaFile(fileName):
    try:
        img = cv2.imread('capcha_c.tif')
        if img.all() != None:
            cv2.imwrite(fileName+".tif", img)
    except IOError:
        print("couldn't save with other name")
    return tif2text(fileName).split('\n')

# This function handles the decision to sell or keep a rune
# input:    none
# output:   none
def keepOrSellRune():
    i = 1
    keep = True
    hasSpeedSub = False
    foundRare = False
    global soldRunes
    global keptRunes

    screenCapture()
    sleepCountdown(2)

    while i > 0:
        i-=1
        global legend
        global hero
        global rare
        # sleepCountdown(2)
        performOCR()
        fileN = crop(1150,350,80,150,"capcha") # Rarity
        convPNG2TIF(fileN)

        fullText = readCapchaFile("rarity")
        print("Rarity:" + str(fullText))
        rarity = ""
        for text in fullText:
            if text.find("Rare") != -1:
                # Sell rune if it's 5* and Rare.
                foundRare = True
                rare+=1
                rarity = "Rare"
            if text.find("Hero") != -1:
                hero+=1
                rarity = "Hero"
            if text.find("Legend") != -1:
                legend+=1
                rarity = "Legend"                
            if text.find("Magic") != -1:
                rarity = "Magic"
            if text.find("Normal") != -1:
                rarity = "Normal"

        if rarity == "" and i == 0:
            clickOther()
            return

        fileN = crop(600,350,300,600,"capcha") # Sub stats
        convPNG2TIF(fileN)

        fullText = readCapchaFile("substats")

        print("Subststs:" + str(fullText))
        for text in fullText:
            if text.find("SPD") != -1 or text.find("SPA") != -1:
                # Keep rune if it has speed sub.
                hasSpeedSub = True

    sixStar = checkSixStar("capcha")

    print("found speed? " + str(hasSpeedSub))
    print("found rare? " + str(foundRare))
    print("found rarity? " + rarity)

    if sixStar:
        if rarity == "Rare" and not hasSpeedSub:
            keep = False
        else:
            keep = True
    else:
        if rarity == "Legend":
            keep = True
        else:
            if  rarity == "Hero" and hasSpeedSub:
                keep = True
            else:
                keep = False

    # Handle the number of runes if a rune was sold
    if  keep == False:
        if  rarity == "Legend":
            legend-=1
        if  rarity == "Hero":
            hero-=1
        if  rarity == "Rare":
            rare-=1
        if  rarity == "Normal":
            rare-=1

    print("keep? " + str(keep))
    if keep == False:
        print("Clicked sell rune")
        tap(random.randint(700,900),random.randint(820,920))
        sleepPrinter(random.uniform(1,3))
        print("Clicked confirmed rune sell")
        tap(random.randint(850,880),random.randint(600,700))
        soldRunes += 1
    else:
        print("Clicked keep rune")
        tap(random.randint(1030,1230),random.randint(820,920))
        keptRunes += 1

# This function handles the death case of a run
# input:    none
# output:   stdio output
def sayNo2Revives():
    global revivedCnt
    revivedCnt = revivedCnt + 1
    print("Clicked no on revive")
    tap(random.randint(1050,1420),random.randint(650,750))
    sleepPrinter(1)
    print("Clicked Randomly")
    tap(random.randint(1310,1310),random.randint(100,200))
    sleepPrinter(1)
    print("Clicked Randomly")
    tap(random.randint(1300,1310),random.randint(100,200))
    sleepPrinter(3)

# This function prints tuple to command line
# input:    tupleWA - tuple for input
# output:   tupleWA in stdio
def print2CMD(tupleWA):
    for t in tupleWA:
        print(t)

# This function prints the file
# input:    tupleWA - tuple for input
# output:   stats.log file
def print2File(tupleWA):
    filename = "stats.log"
    print("logged.")
    file = open(filename,"w")
    for t in tupleWA:
        t = t + "\n"
        file.write(t)
    file.close()

# This function models the stats file before printing to file
# input:    i - Number of run currently running
# output:   stats.log file to defualt library
def printStats(i):
    printable = []
    printable.append("---------------------------------------------------------")
    printable.append("Stats:")
    printable.append("Selling runes? " + str(sellRunes))
    printable.append("Number of runes sold: " + str(soldRunes))
    printable.append("Number of runes kept: " + str(keptRunes))
    printable.append("Number of not runes (scrolls, angelmons etc): " + str(notRuneCnt))
    printable.append("Number of Legend runes: " + str(legend) )
    printable.append("Number of Hero runes: "  + str(hero) )
    printable.append("Number of Rare runes: "  + str(rare) )
    printable.append("Number of K.O.: " + str(revivedCnt))
    printable.append("Total refills: " + str(totalRefills))
    printable.append("Total runs: " + str(i-totalRefills))
    printable.append("Success Rate: " + "%.2f" % round(((i-totalRefills-revivedCnt)/(i))*100,2) )
    printable.append("---------------------------------------------------------")
    # print2CMD(printable)
    print2File(printable)

def clickOther():
    global notRuneCnt
    notRuneCnt = notRuneCnt + 1
    print("it's not a rune!")
    print("Clicked Get Symbol\\angelmon\\scrolls")
    tap(random.randint(950,960),random.randint(850,870))
    sleepPrinter(random.uniform(1,3))
    tap(random.randint(1100,1200),random.randint(710,715))
    sleepPrinter(random.uniform(1,3))

def clickConnect():
    print("Reconnecting...")
    tap(random.randint(670,900),random.randint(670,750))
    sleepPrinter(random.uniform(1,3))
def clickConnectBeforeRun():
    print("Reconnecting for run...")
    tap(random.randint(600,650),random.randint(800,810))
    sleepPrinter(random.uniform(1,3))

def handleAfterMatchDungeon():
    print("Clicked Randomly")
    tap(random.randint(1300,1310),random.randint(190,200))
    sleepPrinter(3)
    print("Clicked Randomly")
    tap(random.randint(1300,1310),random.randint(190,200))
    clickOrSellRunes()

def clickOrSellRunes():
    sleepPrinter(3)
    if sellRunes:
        keepOrSellRune()
    else:
        print("Clicked keep rune")
        tap(random.randint(1030,1230),random.randint(820,920))

def handleAfterMatchRaid():
    sleepPrinter(random.uniform(2,3))
    clickOrSellRunes()
    print("Clicked OK")
    tap(random.randint(1000,1020),random.randint(800,815))

def handleAfterMatchR5():
    return "yay"

def handleArgs(argv):
    try:
        opts, args = getopt.getopt(argv,"fartb",[])
    except getopt.GetoptError:
        print("Arguments mismatch")
    for opt, args in opts:
        if opt == '-f':
            print("Farming runes!")
            return "farm"
        elif opt == '-a':
            print("Farming arena!")
            return "arena"
        elif opt == '-r':
            print("Farming raid!")
            return "r5"
        elif opt == '-b':
            print("Farming beasts!")
            return "beasts"
        elif opt == '-t':
            print("Farming ToA/H!")
            return "TOA"        
        elif opt == '-d':
            print("Farming Dimensional hole!")
            return "dh"
    if  len(args) == 0 or len(opts) == 0:
        print("What are you looking to farm?")
        exit(0)

def startDungeonMode(i, taskType):
    print("Clicked Start")
    tap(random.randint(1460,1780),random.randint(780,840)) # Click on start
    refilled = False
    loopCond = True
    mod = 0
    while loopCond:
        ret = performOCR()
        if ret.find("refill") != -1:
            refillEnergy()
            loopCond = False
            refilled = True

        if ret.find("revive") != -1:
            sayNo2Revives()
            refilled = True
            loopCond = False

        if ret.find("reward") != -1:
            loopCond = False

        if ret.find("grindstone") != -1:
            print("Clicked keep grindstone/gem")
            tap(random.randint(1030,1230),random.randint(820,920))
            sleepPrinter(random.uniform(1,2))
            print("Clicked Continue")
            tap(random.randint(800,850),random.randint(600,650))
            loopCond = False
            return

        if ret.find("correct") != -1:
            return True

        if ret.find("dc") != -1:
            clickConnect()

        if ret.find("dc_before_run") != -1:
            clickConnectBeforeRun()

        mod += 1
        mod = mod %1024
        sys.stdout.write(ret + str(mod) + "\n")
        sys.stdout.flush()

    if refilled == False:
        if  taskType == "farm":
            handleAfterMatchDungeon()
        # elif taskType == "raid":
        #     handleAfterMatchRaid()
        sleepPrinter(random.uniform(2,3))
    sleepPrinter(random.uniform(2,3))
    print("Clicked Continue")
    tap(random.randint(800,850),random.randint(600,650))
    sleepPrinter(random.uniform(1.5,2.5))

def openRewardScreen():
    print("Clicked Randomly")
    sleepCountdown(random.uniform(2,3))
    tap(random.randint(100,110),random.randint(100,200)) # Click on start
    print("Clicked Randomly")
    sleepCountdown(random.uniform(1,2))
    tap(random.randint(100,110),random.randint(100,200)) # Click on start
    print("Clicked Randomly")
    sleepCountdown(random.uniform(2,3))
    tap(random.randint(1160,1260),random.randint(100,200)) # Click on start
    print("Clicked Reward")
    sleepCountdown(random.uniform(1,1.5))
    tap(random.randint(800,850),random.randint(600,650)) # Show the rune itself due to a dumb com2us update

def startRaidMode(i, taskType):
    print("Clicked Start")
    tap(random.randint(1500,1700),random.randint(700,800)) # Click on start
    refilled = False
    loopCond = True
    mod = 0
    while loopCond:
        ret = performOCR()
        if ret.find("refill") != -1:
            refillEnergy()
            loopCond = False
            refilled = True

        if ret.find("beasts_win") != -1:
            openRewardScreen()
            loopCond = False

        if ret.find("correct") != -1:
            return True

        if ret.find("dc") != -1:
            clickConnect()

        if ret.find("dc_before_run") != -1:
            clickConnectBeforeRun()

        mod += 1
        mod = mod %1024
        sys.stdout.write(ret + str(mod) + "\n")
        sys.stdout.flush()

    if refilled == False:
        if taskType == "r5":
            handleAfterMatchR5()
        elif taskType == "beasts":
            handleAfterMatchRaid()
        sleepPrinter(random.uniform(2,3))
    sleepPrinter(random.uniform(2,3))
    print("Clicked Continue")
    tap(random.randint(800,850),random.randint(600,650))
    sleepPrinter(random.uniform(1.5,2.5))

    return

# This function handles the workflow
# input:    argv        - arguments gives in stdio
#           _SellRunes  - a flag to indicate if we want to sell runes
# output:   prints to stdio
def startBot(argv, _SellRunes = False):

    taskType = handleArgs(argv)
    if  taskType == "":
        exit(2)

    i = 0
    while True:
        i += 1
        printStats(i)
        crop2Default() # Reset capcha_c.tif file to avoid reading the same file next iteration

        getScreenCapture()
        if  taskType == "farm" or taskType == "TOA" or taskType == "dh":
            startDungeonMode(i,"farm")
            print("i Count: " + str(i))
        elif taskType == "beasts":
            startRaidMode(i,"beasts")


clearConsole()
startBot(sys.argv[1:])

adb.adbshell('input keyevent 26') # Turn off screen

print("Finished")

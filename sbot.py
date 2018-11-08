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
from adbInterface import adbInterface as adb

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

def tap(x, y):
    command = "input tap " + str(x) + " " + str(y)
    command = str.encode(command)
    adb.adbshell(command.decode('utf-8'))

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

def clearConsole():
    os.system('cls') 

def runImageCheck(imageType):
    args = ["python.exe","classify_image.py","--image_file",".\dataset\\" + imageType + ".jpeg"]
    # print(args)
    return subprocess.Popen(args, shell=True, stdout=subprocess.PIPE)

def sleepPrinter(timeEpoch):
    # print("sleeping for: " + str(timeEpoch) + " seconds")
    sleepCountdown(timeEpoch)

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

def convTIF2PNG(fileName):
    image_file = Image.open(fileName + '.tif').convert('L')
    image_file.save(fileName + '.jpg')

def convPNG2TIF(fileName):
    try: 
        image_file = Image.open(fileName + '.jpg').convert('L')
        image_file.save(fileName + '.tif')
    except IOError:
        print("Error saving from jpg to tif")

def checkSixStar(fileName):
    res = False
    im_gray = cv2.imread(fileName+".jpg", cv2.IMREAD_GRAYSCALE)
    thresh = 127
    im_bw = cv2.threshold(im_gray, thresh, 255, cv2.THRESH_BINARY)[1]
    try:
        if im_bw is not None:
            res = im_bw[363][718] == im_bw[363][732]
            print("Found it to be a 6*? " + str(res))
    except IOError:
        print("No picture found")
    return res

def getScreenCapture():
    screenCapture()
    # Pull image from the phone
    adb.adbpull("/sdcard/SummonerBot/capcha.jpg")
    time.sleep(1)
    return "capcha"

def crop(x,y,h,w,fileName):
    try:
        img = cv2.imread(fileName + '.jpg')
        if img is not None:
            crop_img = img[y:y+h, x:x+w]
            cv2.imwrite(fileName + "_c.jpg", crop_img)
    except IOError:
        print("Could not open file " + fileName)
    return fileName + "_c"

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

def performOCR():
    global totalRefills
    fileN = crop(0,300,1050,1900,getScreenCapture())
    convPNG2TIF(fileN)
    fullText = tif2text(fileN).split('\n')
    for text in fullText:
        if text.find("Not enough Energy") != -1:
            totalRefills += 1
            return "refill"
        if text.find("Revive") != -1:
            return "revive"
        if text.find("correct") != -1:
            return "correct"
        if text.find("count as a loss") != -1:
            return "dc"
        if text.find("connection") != -1:
            return "dc_before_run"            
        if text.find("Reward") != -1:
            return "reward"
        if text.find("Rewand") != -1:
            return "reward"
        if text.find("Rewamdi") != -1:
            return "reward"
        if text.find("Rewamd") != -1:
            return "reward"
            
    print(fullText)

    return "performed OCR reading "
    
def refillEnergy():
    print("Clicked Refill")
    tap(random.randint(690,700),random.randint(600,700))
    sleepPrinter(2)

    print("Clicked recharge energy")
    tap(random.randint(694,696),random.randint(400,500))
    sleepPrinter(5)

    print("Clicked confirm buy")
    tap(random.randint(690,700),random.randint(600,700))
    sleepPrinter(2)

    print("Clicked purchase successful")
    tap(random.randint(840,1090),random.randint(600,700))
    sleepPrinter(2)

    print("Clicked close shop")
    tap(random.randint(850,1050),random.randint(880,980))
    sleepPrinter(2)

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
        performOCR()        
        fileN = crop(1200,350,50,100,"capcha") # Rarity
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

        if rarity == "" and i == 0:
            clickOther()
            return
        
        fileN = crop(600,350,300,600,"capcha") # Sub stats
        convPNG2TIF(fileN)
                
        fullText = readCapchaFile("substats")

        print("Subststs:" + str(fullText))
        for text in fullText:
            if text.find("SPD") != -1:
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

def sayNo2Revives():
    global revivedCnt
    revivedCnt = revivedCnt + 1
    print("Clicked no on revive")
    tap(random.randint(1050,1420),random.randint(650,750))
    sleepPrinter(1)
    print("Clicked Randomly")
    tap(random.randint(1340,1350),random.randint(440,450))
    sleepPrinter(1)
    print("Clicked Randomly")
    tap(random.randint(1300,1350),random.randint(440,450))
    sleepPrinter(3)

def print2CMD(tupleWA):
    for t in tupleWA:
        print(t)

def print2File(tupleWA):
    filename = "stats.log"
    print("logged.")
    file = open(filename,"w")
    for t in tupleWA:
        t = t + "\n"
        file.write(t)
    file.close()

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
    printable.append("Success Rate: " + "%.2f" % round(((i-totalRefills-revivedCnt)/(i-totalRefills))*100,2) )
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

def clickConnect():
    print("Reconnecting...")
    tap(random.randint(670,900),random.randint(670,750)) 
    sleepPrinter(random.uniform(1,3))
def clickConnectBeforeRun():
    print("Reconnecting for run...")
    tap(random.randint(600,650),random.randint(800,810)) 
    sleepPrinter(random.uniform(1,3))

def startBot(_SellRunes = False):
    i = 0
    while True:
        i += 1
        printStats(i)
        crop2Default() # Reset capcha_c.tif file to avoid reading the same file next iteration
        
        getScreenCapture()
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

            if ret.find("correct") != -1:
                return True

            if ret.find("dc") != -1:
                clickConnect()

            if ret.find("dc_before_run") != -1:
                clickConnectBeforeRun

            mod += 1        
            mod = mod %1024
            sys.stdout.write(ret + str(mod) + "\n")
            sys.stdout.flush()        
        
        if refilled == False:
            print("Clicked Randomly")
            tap(random.randint(1300,1350),random.randint(690,700))
            sleepPrinter(1)
            print("Clicked Randomly")
            tap(random.randint(1300,1350),random.randint(690,700))
            sleepPrinter(3)
            if sellRunes:
                keepOrSellRune()
            else:
                print("Clicked keep rune")
                tap(random.randint(1030,1230),random.randint(820,920)) 
            sleepPrinter(random.uniform(2,3))
        sleepPrinter(random.uniform(2,3))    
        print("Clicked Continue")
        tap(random.randint(800,850),random.randint(600,650))
        sleepPrinter(random.uniform(1.5,2.5))
        

clearConsole()
startBot()

adb.adbshell('input keyevent 26') # Turn off screen

print("Finished")
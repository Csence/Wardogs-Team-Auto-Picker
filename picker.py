
import os
import sys

import cv2
import keyboard
import time
import subprocess
from mss import MSS
from title import Title
from utils.screenCapture import captureScreen
from utils.utils import getGameStatus, getMonitorId, clickLeftMouseButton
import utils.imageProcesser as imageProcesser

class Picker: 

    def __init__(self, screen_width, screen_height):
        self.screen_height = screen_height
        self.screen_width = screen_width
        return

    @staticmethod
    def __scale_region(screen_width, screen_height):
        base_width = 1920
        base_height = 1080

        region = (
            int(720 * screen_width / base_width),
            int(400 * screen_height / base_height),
            int(480 * screen_width / base_width),
            int(300 * screen_height / base_height)
        )

        return region

    @staticmethod
    def __scale_region_ingame(screen_width, screen_height):
        base_width = 1920
        base_height = 1080

        region = (
            int(1850 * screen_width / base_width),
            int(1000 * screen_height / base_height),
            int(50 * screen_width / base_width),
            int(50 * screen_height / base_height)
        )

        return region

    def pick_team(self, images):
        
        img, inGameImg = images
        
        running, pid = getGameStatus()
        
        if not running:
            print("Wardogs is not running. Please start the game and try again.")
            subprocess.call("cls", shell=True)
            #os.system("cls")
            print(Title.show_title())
            return

        monitorId = getMonitorId(pid)
        needleImg = imageProcesser.loadNeedleImage(img)
        needleInGameImg = imageProcesser.loadNeedleImage(inGameImg)
        
        #subprocess.call("cls")
        print("Team selection in progress...")

        with MSS() as sct:
            point = None
            monitorData = sct.monitors[monitorId]
            isInGame = False
            
            while point is None:
                if keyboard.is_pressed("esc"):
                    return

                haystackImg = captureScreen(sct, monitorId)
                #cv2.imshow("Haystack Image", haystackImg)
                #cv2.waitKey()  # Add a small delay to allow the image to be displayed
                try:
                    region = self.__scale_region(self.screen_width, self.screen_height)
                    point = imageProcesser.locateCenterAndMove(haystackImg, needleImg, threshold=0.9, monitorXY=(monitorData["left"], monitorData["top"]), regionXY=(region[0], region[1]))
                except ValueError as e:
                    #supress the exception and continue searching for the needle in the haystack
                    print("")

            while not isInGame:
                if keyboard.is_pressed("esc"):
                    return

                haystackImg = captureScreen(sct, monitorId, inGameScale=True)
                #imageProcesser.show_image(haystackImg, window_name="Haystack Image")
                #cv2.waitKey()  # Add a small delay to allow the image to be displayed
                try:
                    region = self.__scale_region_ingame(self.screen_width, self.screen_height)
                    imageProcesser.locateCenterAndMove(haystackImg, needleInGameImg, threshold=0.7, monitorXY=(monitorData["left"], monitorData["top"]), regionXY=(region[0], region[1]))
                    isInGame = True
                except ValueError as e:
                    #supress the exception and continue searching for the needle in the haystack
                    print("")

                if isInGame:
                    break

                clickLeftMouseButton()
                time.sleep(0.4)






        subprocess.call("cls")
        print("You entered the selected team!\n" \
        "Going back to the menu!")
        time.sleep(4)
        subprocess.call("cls")
        print(Title.show_title())

        return
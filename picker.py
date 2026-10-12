import keyboard
import time
import subprocess
from mss import MSS
from title import Title
from utils.screenCapture import captureScreen
from utils.utils import getGameStatus, getMonitorId, clickLeftMouseButton
import utils.imageProcesser as imageProcesser
from utils.utils import scale_region, scale_region_ingame

class Picker:

    @staticmethod
    def pick_team(images):

        img, inGameImg = images
  
        running, pid = getGameStatus()

        if not running:
            print("Wardogs is not running. Please start the game and try again.")
            subprocess.call("cls", shell=True)
            Title.show_title()
            return

        monitorId = getMonitorId(pid)
        needleImg = imageProcesser.loadNeedleImage(img)
        needleInGameImg = imageProcesser.loadNeedleImage(inGameImg)

        subprocess.call("cls", shell=True)
        print("Team selection in progress...")

        with MSS() as sct:
            point = None
            monitorData = sct.monitors[monitorId]
            isInGame = False

            while point is None:
                if keyboard.is_pressed("esc"):
                    return

                haystackImg = captureScreen(sct, monitorId)
                try:
                    region = scale_region(monitorData["width"], monitorData["height"])
                    point = imageProcesser.locateCenterAndMove(haystackImg, needleImg, threshold=0.9, monitorXY=(monitorData["left"], monitorData["top"]), regionXY=(region[0], region[1]))
                except ValueError as e:
                    #supress the exception and continue searching for the needle in the haystack
                    pass

            while not isInGame:
                if keyboard.is_pressed("esc"):
                    return

                haystackImg = captureScreen(sct, monitorId, inGameScale=True)
                try:
                    region = scale_region_ingame(monitorData["width"], monitorData["height"])
                    imageProcesser.locateCenter(haystackImg, needleInGameImg, threshold=0.6, monitorXY=(monitorData["left"], monitorData["top"]), regionXY=(region[0], region[1]))
                    isInGame = True
                except ValueError as e:
                    #supress the exception and continue searching for the needle in the haystack
                    pass

                if isInGame:
                    break

                clickLeftMouseButton()
                time.sleep(0.4)

        subprocess.call("cls", shell=True)
        print("You entered the selected team!\n" \
        "Going back to the menu!...")
        time.sleep(15)
        subprocess.call("cls", shell=True)
        Title.show_title()

        return
lazy import keyboard
lazy import time
lazy import subprocess
lazy from mss import MSS
lazy from title import Title
lazy from utils.screenCapture import ScreenCapture
lazy from utils.utils import Utils
lazy from utils.imageProcesser import ImageProcesser

class Picker:

    @staticmethod
    def pick_team(images) -> None:

        img, inGameImg = images
  
        running, pid = Utils.getGameStatus()

        if not running:
            print("Wardogs is not running. Please start the game and try again.")
            subprocess.call("cls", shell=True)
            Title.show_title()
            return

        monitorId = Utils.getMonitorId(pid)
        imageProcesser = ImageProcesser()
        needleImg = imageProcesser.loadNeedleImage(img)
        needleInGameImg = imageProcesser.loadNeedleImage(inGameImg)

        subprocess.call("cls", shell=True)
        print("Team selection in progress...")

        with MSS() as sct:
            monitorData = sct.monitors[monitorId]
            utils = Utils(sct, monitorData["width"], monitorData["height"])
            screenCapture = ScreenCapture(sct, utils)
            point = None
            isInGame = False

            while point is None:
                if keyboard.is_pressed("esc"):
                    return

                haystackImg = screenCapture.captureScreen(monitorId)
                try:
                    region = utils.scale_region()
                    point = imageProcesser.locateCenterAndMove(haystackImg, needleImg, threshold=0.9, monitorXY=(monitorData["left"], monitorData["top"]), regionXY=(region[0], region[1]))
                except ValueError as e:
                    #supress the exception and continue searching for the needle in the haystack
                    pass

            while not isInGame:
                if keyboard.is_pressed("esc"):
                    return

                haystackImg = screenCapture.captureScreen(monitorId, inGameScale=True)
                try:
                    region = utils.scale_region_ingame()
                    imageProcesser.locateCenter(haystackImg, needleInGameImg, threshold=0.6)
                    isInGame = True
                except ValueError as e:
                    #supress the exception and continue searching for the needle in the haystack
                    pass

                if isInGame:
                    break

                Utils.clickLeftMouseButton()
                time.sleep(0.4)

        subprocess.call("cls", shell=True)
        print("You entered the selected team!\n" \
        "Going back to the menu!...")
        time.sleep(15)
        subprocess.call("cls", shell=True)
        Title.show_title()

        return None
import pyautogui
import keyboard
import time
import subprocess
from title import Title

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
        x = None
        isIngame = False

        subprocess.call("cls")
        print("Team selection in progress...")

        while x == None:
            if keyboard.is_pressed("esc"):
                return
            
            try:
                x, y = pyautogui.locateCenterOnScreen(images[0], confidence=0.9, grayscale=True, region=self.__scale_region(self.screen_width, self.screen_height))
            except pyautogui.ImageNotFoundException:
                x = None

            time.sleep(0.05)

        while isIngame == False:
            try:
                isIngame = pyautogui.locateCenterOnScreen(images[1], confidence=0.9, grayscale=True, region=self.__scale_region_ingame(self.screen_width, self.screen_height))
            except pyautogui.ImageNotFoundException:
                isIngame = False

            if keyboard.is_pressed("esc"):
                return
                
            pyautogui.moveTo(x,y)
            pyautogui.leftClick()
            time.sleep(0.09)

        subprocess.call("cls")
        print("You entered the selected team!\n" \
        "Going back to the menu!")
        time.sleep(4)
        subprocess.call("cls")
        print(Title.show_title())

        return
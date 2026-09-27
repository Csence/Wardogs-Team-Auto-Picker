from picker import Picker
import keyboard
from teams import Teams
from title import Title
import cv2
import pyautogui

screen_width, screen_height = pyautogui.size()

print(Title.show_title())

picker = Picker(screen_width, screen_height)

keyboard.add_hotkey("f1", lambda: picker.pick_team(Teams.LONESTAR.value))
keyboard.add_hotkey("f2", lambda: picker.pick_team(Teams.VALKYRA.value))
keyboard.add_hotkey("f3", lambda: picker.pick_team(Teams.MANTICORE.value))
keyboard.wait("esc")
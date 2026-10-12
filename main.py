import keyboard
from picker import Picker
from teams import Teams
from title import Title

Title.show_title()

picker = Picker()

keyboard.add_hotkey("f1", lambda: picker.pick_team(Teams.LONESTAR.value))
keyboard.add_hotkey("f2", lambda: picker.pick_team(Teams.VALKYRA.value))
keyboard.add_hotkey("f3", lambda: picker.pick_team(Teams.MANTICORE.value))
keyboard.wait("esc")
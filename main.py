lazy import keyboard
lazy from picker import Picker
lazy from teams import Teams
lazy from title import Title

Title.show_title()

picker = Picker()

keyboard.add_hotkey("f1", lambda: picker.start(Teams.LONESTAR.value))
keyboard.add_hotkey("f2", lambda: picker.start(Teams.VALKYRA.value))
keyboard.add_hotkey("f3", lambda: picker.start(Teams.MANTICORE.value))
keyboard.wait("esc")
picker.stop()
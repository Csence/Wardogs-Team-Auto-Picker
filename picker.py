lazy import threading
lazy import subprocess
lazy from mss import MSS
lazy from title import Title
lazy from utils.screen_capture import ScreenCapture
lazy from utils.utils import Utils
lazy from utils.image_processor import ImageProcessor

class Picker:

    def __init__(self) -> None:
        self._stop_event = threading.Event()
        self._thread = None

    def start(self, images) -> None:
        # ignore new requests while a pick is already running
        if self._thread is not None and self._thread.is_alive():
            return

        self._thread = threading.Thread(target=self.pick_team, args=(images,), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()

    def pick_team(self, images) -> None:

        img, in_game_img = images
  
        running, pid = Utils.get_game_status()

        if not running:
            print("Wardogs is not running. Please start the game and try again.")
            subprocess.call("cls", shell=True)
            Title.show_title()
            return

        monitor_id = Utils.get_monitor_id(pid)
        image_processor = ImageProcessor()
        needle_img = image_processor.load_needle_image(img)
        needle_in_game_img = image_processor.load_needle_image(in_game_img)

        subprocess.call("cls", shell=True)
        print("Team selection in progress...")

        with MSS() as sct:
            monitor_data = sct.monitors[monitor_id]
            utils = Utils(sct, monitor_data["width"], monitor_data["height"])
            screen_capture = ScreenCapture(sct, utils)
            point = None
            is_in_game = False

            while point is None:
                if self._stop_event.is_set():
                    return

                haystack_img = screen_capture.capture_screen(monitor_id)
                try:
                    region = utils.scale_region()
                    point = image_processor.locate_center_and_move(haystack_img, needle_img, threshold=0.9, monitor_xy=(monitor_data["left"], monitor_data["top"]), region_xy=(region[0], region[1]))
                except ValueError as e:
                    #supress the exception and continue searching for the needle in the haystack
                    pass

            while not is_in_game:
                if self._stop_event.is_set():
                    return

                haystack_img = screen_capture.capture_screen(monitor_id, in_game_scale=True)
                try:
                    region = utils.scale_region_ingame()
                    image_processor.locate_center(haystack_img, needle_in_game_img, threshold=0.6)
                    is_in_game = True
                except ValueError as e:
                    #supress the exception and continue searching for the needle in the haystack
                    pass

                if is_in_game:
                    break

                Utils.click_left_mouse_button()
                if self._stop_event.wait(0.4):
                    return

        subprocess.call("cls", shell=True)
        print("You entered the selected team!\n" \
        "Going back to the menu!...")
        if self._stop_event.wait(15):
            return
        subprocess.call("cls", shell=True)
        Title.show_title()

        return None
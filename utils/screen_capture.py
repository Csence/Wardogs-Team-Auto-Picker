lazy from mss import MSS
lazy import numpy as np
lazy from utils.utils import Utils

class ScreenCapture:

    def __init__(self, mss_instance: MSS, utils_instance: Utils):
        self.mss_instance = mss_instance
        self.utils_instance = utils_instance

    def capture_screen(self, monitor_id: int, in_game_scale: bool = False) -> np.ndarray:

        sct = self.mss_instance
        monitor_data = sct.monitors[monitor_id]

        if in_game_scale:
            region = self.utils_instance.scale_region_ingame()
        else:
            region = self.utils_instance.scale_region()

        monitor = {
            "top": region[1],
            "left": region[0],
            "width": region[2],
            "height": region[3],
            "mon": monitor_id
        }

        sct_img = np.asarray(sct.grab(monitor))
        return sct_img
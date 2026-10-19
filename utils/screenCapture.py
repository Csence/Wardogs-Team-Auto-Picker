lazy from mss import MSS
lazy import numpy as np
lazy from utils.utils import Utils

class ScreenCapture:

    def __init__(self, mssInstance: MSS, utilsInstance: Utils):
        self.mssInstance = mssInstance
        self.utilsInstance = utilsInstance

    def captureScreen(self, monitorId: int, inGameScale: bool = False) -> np.ndarray:

        sct = self.mssInstance
        monitorData = sct.monitors[monitorId]

        if inGameScale:
            region = self.utilsInstance.scale_region_ingame()
        else:
            region = self.utilsInstance.scale_region()

        monitor = {
            "top": region[1],
            "left": region[0],
            "width": region[2],
            "height": region[3],
            "mon": monitorId
        }

        sct_img = np.asarray(sct.grab(monitor))
        return sct_img
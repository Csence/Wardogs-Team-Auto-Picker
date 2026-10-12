from mss import MSS
import numpy as np
from utils.utils import scale_region, scale_region_ingame

def captureScreen(mssInstance: MSS, monitorId: int, inGameScale: bool = False):

    sct = mssInstance
    monitorData = sct.monitors[monitorId]

    if inGameScale:
        region = scale_region_ingame(monitorData["width"], monitorData["height"])
    else:
        region = scale_region(monitorData["width"], monitorData["height"])

    monitor = {
        "top": region[1],
        "left": region[0],
        "width": region[2],
        "height": region[3],
        "mon": monitorId
    }

    sct_img = np.asarray(sct.grab(monitor))
    return sct_img
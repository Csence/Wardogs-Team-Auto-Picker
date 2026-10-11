from mss import MSS

import numpy as np

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


def captureScreen(mssInstance: MSS, monitorId: int, inGameScale: bool = False):
    sct = mssInstance
    # Get information about the primary monitor
    monitorData = sct.monitors[monitorId]
    #output = "sct-{top}x{left}_{width}x{height}.png".format(**monitor)

    print(sct.monitors)

    if inGameScale:
        region = __scale_region_ingame(monitorData["width"], monitorData["height"])
    else:
        region = __scale_region(monitorData["width"], monitorData["height"])

    #print(region[0], region[1])

    monitor = {
        "top": region[1],
        "left": region[0],
        "width": region[2],
        "height": region[3],
        "mon": monitorId
    }


    # Print the monitor information
    print(f"Monitor Info: {monitor}")
    sct_img = np.asarray(sct.grab(monitor))
    #png = mss.tools.to_png(sct_img.rgb, sct_img.size)
    return sct_img

"""
with MSS() as mss_instance:
    img = captureScreen(mss_instance, 1)

    imageProcesser.show_image(img)
"""

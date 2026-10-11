import cv2
import numpy
import utils.utils as utils

def show_image(image, window_name='Image'):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cv2.imshow("OpenCV image",image)
    cv2.waitKey()

def loadNeedleImage(path):
    needle = cv2.imread(path)
    if needle is None:
        raise ValueError(f"Could not load image from path: {path}")
    return needle


def locateCenterAndMove(haystack, needle, threshold=0.8, monitorXY=(0, 0), regionXY=(0,0)):
    haystack = cv2.cvtColor(haystack, cv2.COLOR_BGR2GRAY)
    needle = cv2.cvtColor(needle, cv2.COLOR_BGR2GRAY)

    monitorX, monitorY = monitorXY
    regionX, regionY = regionXY

    if haystack.shape[0] < needle.shape[0] or haystack.shape[1] < needle.shape[1]:
        raise ValueError("needle dimension(s) exceed the haystack image")

    result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if max_val >= threshold:
        print(f"Found needle at {max_loc[0] + needle.shape[1] // 2}, {max_loc[1] + needle.shape[0] // 2} with confidence {max_val}")
        utils.moveMouseToPosition(monitorX + regionX + max_loc[0] + needle.shape[1] // 2, monitorY + regionY + max_loc[1] + needle.shape[0] // 2)
        return max_loc
    else: 
        raise ValueError("needle not found in haystack with the given threshold")
    
    return None

#locateCenter(cv2.imread("D:\\Projects\\Wardogs-Team-Auto-Picker\\utils\\hay (2).png"), loadNeedleImage("D:\\Projects\\Wardogs-Team-Auto-Picker\\utils\\needle (2).png"), threshold=0.99)
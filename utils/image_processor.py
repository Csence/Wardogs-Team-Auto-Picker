lazy import cv2
lazy from utils.utils import Utils

class ImageProcessor:

    def __init__(self):
        pass

    @staticmethod
    def load_needle_image(path: str) -> cv2.Mat | ValueError:
        needle = cv2.imread(path)
        if needle is None:
            raise ValueError(f"Could not load image from path: {path}")
        return needle
    
    @staticmethod
    def locate_center_and_move(haystack, needle, threshold=0.8, monitor_xy=(0, 0), region_xy=(0,0)) -> tuple[int, int] | ValueError:
        haystack = cv2.cvtColor(haystack, cv2.COLOR_BGR2GRAY)
        needle = cv2.cvtColor(needle, cv2.COLOR_BGR2GRAY)

        monitor_x, monitor_y = monitor_xy
        region_x, region_y = region_xy

        if haystack.shape[0] < needle.shape[0] or haystack.shape[1] < needle.shape[1]:
            raise ValueError("needle dimension(s) exceed the haystack image")

        result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            Utils.move_mouse_to_position(monitor_x + region_x + max_loc[0] + needle.shape[1] // 2, monitor_y + region_y + max_loc[1] + needle.shape[0] // 2)
            return max_loc
        else: 
            raise ValueError("needle not found in haystack with the given threshold")

    @staticmethod
    def locate_center(haystack, needle, threshold=0.8) -> tuple[int, int] | ValueError:
        haystack = cv2.cvtColor(haystack, cv2.COLOR_BGR2GRAY)
        needle = cv2.cvtColor(needle, cv2.COLOR_BGR2GRAY)

        if haystack.shape[0] < needle.shape[0] or haystack.shape[1] < needle.shape[1]:
            raise ValueError("needle dimension(s) exceed the haystack image")

        result = cv2.matchTemplate(haystack, needle, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            #print(f"Found needle at {max_loc[0] + needle.shape[1] // 2}, {max_loc[1] + needle.shape[0] // 2} with confidence {max_val}")
            return max_loc
        else: 
            raise ValueError("needle not found in haystack with the given threshold")
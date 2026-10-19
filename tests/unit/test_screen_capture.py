import numpy as np

from tests.conftest import FakeMSS
from utils.screen_capture import ScreenCapture
from utils.utils import Utils


class TestCaptureScreen:

    def test_captures_menu_region(self, fake_monitors):
        sct = FakeMSS(fake_monitors)
        screen_capture = ScreenCapture(sct, Utils(sct, 1920, 1080))

        image = screen_capture.capture_screen(1)

        assert sct.grabbed == [{"top": 400, "left": 720, "width": 480, "height": 300, "mon": 1}]
        assert isinstance(image, np.ndarray)
        assert image.shape == (300, 480, 4)

    def test_captures_ingame_region(self, fake_monitors):
        sct = FakeMSS(fake_monitors)
        screen_capture = ScreenCapture(sct, Utils(sct, 1920, 1080))

        image = screen_capture.capture_screen(2, in_game_scale=True)

        assert sct.grabbed == [{"top": 1000, "left": 1850, "width": 50, "height": 50, "mon": 2}]
        assert image.shape == (50, 50, 4)

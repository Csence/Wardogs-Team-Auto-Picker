from unittest import mock

import numpy as np
import pytest

from tests.conftest import make_haystack, make_noise
from utils.image_processor import ImageProcessor
from utils.utils import Utils


@pytest.fixture
def needle():
    # a checkerboard-like pattern so template matching has a clear peak
    rng = np.random.default_rng(42)
    return rng.integers(0, 256, size=(20, 30, 3), dtype=np.uint8)


class TestLoadNeedleImage:

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(ValueError, match="Could not load image"):
            ImageProcessor.load_needle_image(str(tmp_path / "missing.png"))


class TestLocateCenter:

    def test_finds_needle_location(self, needle):
        haystack = make_haystack(needle, 200, 150, x=70, y=40)
        assert ImageProcessor.locate_center(haystack, needle, threshold=0.9) == (70, 40)

    def test_needle_not_present_raises(self, needle):
        with pytest.raises(ValueError, match="not found"):
            ImageProcessor.locate_center(make_noise(200, 150), needle, threshold=0.9)

    def test_needle_bigger_than_haystack_raises(self, needle):
        with pytest.raises(ValueError, match="exceed"):
            ImageProcessor.locate_center(make_noise(10, 10), needle)


class TestLocateCenterAndMove:

    def test_moves_mouse_to_needle_center_with_offsets(self, needle):
        haystack = make_haystack(needle, 200, 150, x=70, y=40)

        with mock.patch.object(Utils, "move_mouse_to_position") as move_mouse:
            location = ImageProcessor.locate_center_and_move(haystack, needle, threshold=0.9, monitor_xy=(1920, 0), region_xy=(720, 400))

        assert location == (70, 40)
        # monitor + region + match location + half the needle size (30x20)
        move_mouse.assert_called_once_with(1920 + 720 + 70 + 15, 0 + 400 + 40 + 10)

    def test_does_not_move_mouse_when_not_found(self, needle):
        with mock.patch.object(Utils, "move_mouse_to_position") as move_mouse:
            with pytest.raises(ValueError, match="not found"):
                ImageProcessor.locate_center_and_move(make_noise(200, 150), needle, threshold=0.9)

        move_mouse.assert_not_called()

    def test_needle_bigger_than_haystack_raises(self, needle):
        with mock.patch.object(Utils, "move_mouse_to_position") as move_mouse:
            with pytest.raises(ValueError, match="exceed"):
                ImageProcessor.locate_center_and_move(make_noise(10, 10), needle)

        move_mouse.assert_not_called()

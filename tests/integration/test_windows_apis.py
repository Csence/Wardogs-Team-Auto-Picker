"""
Calls the real screen capture and Windows APIs. The game does not need to be running.
"""
import numpy as np
import pytest
import win32api
from mss import MSS

from utils.screen_capture import ScreenCapture
from utils.utils import Utils

pytestmark = pytest.mark.integration


@pytest.fixture
def primary_screen():
    with MSS() as sct:
        monitor_data = sct.monitors[1]
        yield sct, Utils(sct, monitor_data["width"], monitor_data["height"])


def test_capture_menu_region(primary_screen):
    sct, utils = primary_screen
    _, _, width, height = utils.scale_region()

    image = ScreenCapture(sct, utils).capture_screen(1)

    assert isinstance(image, np.ndarray)
    assert image.shape == (height, width, 4)
    assert image.dtype == np.uint8


def test_capture_ingame_region(primary_screen):
    sct, utils = primary_screen
    _, _, width, height = utils.scale_region_ingame()

    image = ScreenCapture(sct, utils).capture_screen(1, in_game_scale=True)

    assert image.shape == (height, width, 4)


def test_get_monitor_position_of_primary_monitor(primary_screen):
    sct, utils = primary_screen
    assert utils.get_monitor_position(1) == (sct.monitors[1]["left"], sct.monitors[1]["top"])


def test_get_game_status_returns_consistent_result():
    running, pid = Utils.get_game_status()

    assert isinstance(running, bool)
    if running:
        assert isinstance(pid, int) and pid > 0
    else:
        assert pid is None


def test_get_monitor_id_for_process_without_window():
    # PID 4 is the Windows System process, which never has a visible window
    assert isinstance(Utils.get_monitor_id(4), Exception)


def test_move_mouse_to_position():
    try:
        original = win32api.GetCursorPos()
    except win32api.error as e:
        pytest.skip(f"no interactive desktop for the mouse: {e}")

    try:
        Utils.move_mouse_to_position(10, 10)
        assert win32api.GetCursorPos() == (10, 10)
    finally:
        win32api.SetCursorPos(original)

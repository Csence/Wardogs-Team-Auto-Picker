from types import SimpleNamespace
from unittest import mock

import pytest

from tests.conftest import FakeMSS
from utils import utils as utils_module
from utils.utils import Utils

APP_NAME = "WardogsClient-Win64-Shipping.exe"


def fake_process(name):
    return SimpleNamespace(name=lambda: name)


class TestScaleRegion:

    @pytest.mark.parametrize("width, height, expected", [
        (1920, 1080, (720, 400, 480, 300)),
        (2560, 1440, (960, 533, 640, 400)),
        (3840, 2160, (1440, 800, 960, 600)),
        (1280, 720, (480, 266, 320, 200)),
    ])
    def test_scale_region(self, width, height, expected):
        assert Utils(None, width, height).scale_region() == expected

    @pytest.mark.parametrize("width, height, expected", [
        (1920, 1080, (1850, 1000, 50, 50)),
        (2560, 1440, (2466, 1333, 66, 66)),
        (3840, 2160, (3700, 2000, 100, 100)),
    ])
    def test_scale_region_ingame(self, width, height, expected):
        assert Utils(None, width, height).scale_region_ingame() == expected

    def test_regions_stay_inside_screen(self):
        for width, height in [(1280, 720), (1920, 1080), (2560, 1440), (3440, 1440), (3840, 2160)]:
            utils = Utils(None, width, height)
            for left, top, region_width, region_height in (utils.scale_region(), utils.scale_region_ingame()):
                assert left + region_width <= width
                assert top + region_height <= height


class TestGetMonitorPosition:

    def test_returns_left_and_top_of_monitor(self, fake_monitors):
        utils = Utils(FakeMSS(fake_monitors), 1920, 1080)
        assert utils.get_monitor_position(2) == (1920, 0)
        assert utils.get_monitor_position(1) == (0, 0)


class TestGetGameStatus:

    def run(self, pids, processes):
        def process(pid):
            result = processes[pid]
            if isinstance(result, Exception):
                raise result
            return result

        with mock.patch.object(utils_module.win32process, "EnumProcesses", return_value=pids), \
             mock.patch.object(utils_module.psutil, "Process", side_effect=process) as process_mock:
            return Utils.get_game_status(), process_mock

    def test_finds_running_game(self):
        (running, pid), _ = self.run([0, 4, 100, 200], {100: fake_process("explorer.exe"), 200: fake_process(APP_NAME)})
        assert (running, pid) == (True, 200)

    def test_name_match_is_case_insensitive(self):
        (running, pid), _ = self.run([300], {300: fake_process(APP_NAME.upper())})
        assert (running, pid) == (True, 300)

    def test_game_not_running(self):
        (running, pid), _ = self.run([100], {100: fake_process("explorer.exe")})
        assert (running, pid) == (False, None)

    def test_skips_idle_and_system_process(self):
        _, process_mock = self.run([0, 4, 100], {100: fake_process("explorer.exe")})
        process_mock.assert_called_once_with(100)

    def test_ignores_processes_that_cannot_be_read(self):
        (running, pid), _ = self.run([100, 200], {100: PermissionError("access denied"), 200: fake_process(APP_NAME)})
        assert (running, pid) == (True, 200)


class TestGetMonitorId:

    def run(self, windows, process_id):
        def enum_windows(callback, extra):
            for hwnd in windows:
                callback(hwnd, extra)

        with mock.patch.object(utils_module.win32gui, "EnumWindows", side_effect=enum_windows), \
             mock.patch.object(utils_module.win32gui, "IsWindowVisible", side_effect=lambda hwnd: windows[hwnd]["visible"]), \
             mock.patch.object(utils_module.win32process, "GetWindowThreadProcessId", side_effect=lambda hwnd: (0, windows[hwnd]["pid"])), \
             mock.patch.object(utils_module.win32api, "MonitorFromWindow", side_effect=lambda hwnd, flag: hwnd), \
             mock.patch.object(utils_module.win32api, "GetMonitorInfo", side_effect=lambda handle: {"Device": windows[handle]["device"]}):
            return Utils.get_monitor_id(process_id)

    def test_returns_monitor_of_game_window(self):
        windows = {
            1: {"visible": True, "pid": 10, "device": r"\\.\DISPLAY1"},
            2: {"visible": True, "pid": 20, "device": r"\\.\DISPLAY2"},
        }
        assert self.run(windows, 20) == 2

    def test_ignores_hidden_windows(self):
        windows = {
            1: {"visible": False, "pid": 20, "device": r"\\.\DISPLAY2"},
            2: {"visible": True, "pid": 20, "device": r"\\.\DISPLAY1"},
        }
        assert self.run(windows, 20) == 1

    def test_no_window_for_process(self):
        windows = {1: {"visible": True, "pid": 10, "device": r"\\.\DISPLAY1"}}
        assert isinstance(self.run(windows, 99), Exception)


class TestMouse:

    def test_move_mouse_to_position(self):
        with mock.patch.object(utils_module.win32api, "SetCursorPos") as set_cursor_pos:
            Utils.move_mouse_to_position(100, 200)
        set_cursor_pos.assert_called_once_with((100, 200))

    def test_click_left_mouse_button_presses_then_releases(self):
        with mock.patch.object(utils_module.win32api, "mouse_event") as mouse_event, \
             mock.patch.object(utils_module.time, "sleep"):
            Utils.click_left_mouse_button()

        win32con = utils_module.win32con
        assert mouse_event.call_args_list == [
            mock.call(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0),
            mock.call(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0),
        ]

"""
Runs a whole pick through the real Picker, ImageProcessor, ScreenCapture and Utils with the real team images.
Only the game check, the screen frames and the mouse are faked.
"""
from unittest import mock

import pytest

import picker as picker_module
from picker import Picker
from teams import Teams
from tests.conftest import FakeMSS, make_haystack, make_noise
from utils.image_processor import ImageProcessor
from utils.utils import Utils

pytestmark = pytest.mark.integration


class GameScreen(FakeMSS):
    """Shows the team menu, then switches to in-game after a number of clicks."""

    def __init__(self, monitors, team, clicks_until_ingame):
        super().__init__(monitors)
        menu_needle = ImageProcessor.load_needle_image(team.value[0])
        ingame_needle = ImageProcessor.load_needle_image(team.value[1])
        utils = Utils(None, monitors[1]["width"], monitors[1]["height"])
        _, _, menu_width, menu_height = utils.scale_region()
        _, _, ingame_width, ingame_height = utils.scale_region_ingame()

        self.menu_frame = make_haystack(menu_needle, menu_width, menu_height, x=100, y=50)
        self.ingame_frame = make_haystack(ingame_needle, ingame_width, ingame_height, x=10, y=10)
        self.loading_frame = make_noise(ingame_width, ingame_height)
        self.menu_width = menu_width
        self.clicks_until_ingame = clicks_until_ingame
        self.clicks = 0

    def click(self):
        self.clicks += 1

    def grab(self, monitor):
        self.grabbed.append(monitor)
        if monitor["width"] == self.menu_width:
            return self.menu_frame
        if self.clicks >= self.clicks_until_ingame:
            return self.ingame_frame
        return self.loading_frame


@pytest.mark.parametrize("team", list(Teams), ids=lambda team: team.name)
def test_pick_team_end_to_end(team, fake_monitors):
    screen = GameScreen(fake_monitors, team, clicks_until_ingame=3)
    picker = Picker()

    with mock.patch.object(picker_module, "MSS", return_value=screen), \
         mock.patch.object(picker_module, "subprocess"), \
         mock.patch.object(picker_module.Title, "show_title"), \
         mock.patch.object(Utils, "get_game_status", return_value=(True, 1234)), \
         mock.patch.object(Utils, "get_monitor_id", return_value=2), \
         mock.patch.object(Utils, "move_mouse_to_position") as move_mouse, \
         mock.patch.object(Utils, "click_left_mouse_button", side_effect=screen.click), \
         mock.patch.object(picker._stop_event, "wait", return_value=False):
        picker.pick_team(team.value)

    menu_needle = ImageProcessor.load_needle_image(team.value[0])
    # monitor 2 starts at x=1920, the menu region at (720, 400), the button at (100, 50) inside it
    move_mouse.assert_called_once_with(1920 + 720 + 100 + menu_needle.shape[1] // 2, 0 + 400 + 50 + menu_needle.shape[0] // 2)
    assert screen.clicks == 3


def test_esc_stops_pick_running_on_thread(fake_monitors):
    # the in-game icon never shows up, so the pick would click forever without stop()
    screen = GameScreen(fake_monitors, Teams.LONESTAR, clicks_until_ingame=10**9)
    picker = Picker()

    with mock.patch.object(picker_module, "MSS", return_value=screen), \
         mock.patch.object(picker_module, "subprocess"), \
         mock.patch.object(picker_module.Title, "show_title"), \
         mock.patch.object(Utils, "get_game_status", return_value=(True, 1234)), \
         mock.patch.object(Utils, "get_monitor_id", return_value=1), \
         mock.patch.object(Utils, "move_mouse_to_position"), \
         mock.patch.object(Utils, "click_left_mouse_button", side_effect=screen.click):
        picker.start(Teams.LONESTAR.value)
        picker._thread.join(1)
        assert picker._thread.is_alive()
        assert screen.clicks >= 1

        picker.stop()
        picker._thread.join(1)

    assert not picker._thread.is_alive()

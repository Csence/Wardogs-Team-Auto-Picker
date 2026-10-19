import threading
from unittest import mock

import numpy as np
import pytest

import picker as picker_module
from picker import Picker
from tests.conftest import FakeMSS

IMAGES = ("menu.png", "ingame.png")


@pytest.fixture
def patched(fake_monitors):
    """Patch everything Picker talks to, so pick_team runs without the game, screen or mouse."""

    with mock.patch.object(picker_module, "subprocess") as subprocess_mock, \
         mock.patch.object(picker_module, "Title") as title_mock, \
         mock.patch.object(picker_module, "MSS", return_value=FakeMSS(fake_monitors)), \
         mock.patch.object(picker_module, "ImageProcessor") as image_processor_cls, \
         mock.patch.object(picker_module, "ScreenCapture") as screen_capture_cls, \
         mock.patch.object(picker_module.Utils, "get_game_status", return_value=(True, 1234)) as get_game_status, \
         mock.patch.object(picker_module.Utils, "get_monitor_id", return_value=1) as get_monitor_id, \
         mock.patch.object(picker_module.Utils, "click_left_mouse_button") as click:
        image_processor = image_processor_cls.return_value
        image_processor.load_needle_image.side_effect = lambda path: np.zeros((1, 1, 3), dtype=np.uint8)
        screen_capture = screen_capture_cls.return_value
        screen_capture.capture_screen.return_value = np.zeros((1, 1, 4), dtype=np.uint8)

        yield mock.Mock(
            subprocess=subprocess_mock,
            title=title_mock,
            image_processor=image_processor,
            screen_capture=screen_capture,
            get_game_status=get_game_status,
            get_monitor_id=get_monitor_id,
            click=click,
        )


def no_wait_picker():
    picker = Picker()
    # skip the real waits (0.4 s between clicks and 15 s before going back to the menu)
    picker._stop_event = mock.Mock(is_set=mock.Mock(return_value=False), wait=mock.Mock(return_value=False))
    return picker


class TestPickTeam:

    def test_returns_when_game_not_running(self, patched):
        patched.get_game_status.return_value = (False, None)

        Picker().pick_team(IMAGES)

        patched.get_monitor_id.assert_not_called()
        patched.screen_capture.capture_screen.assert_not_called()
        patched.title.show_title.assert_called_once()

    def test_full_pick_flow(self, patched):
        # the team button is found on the 3rd capture, the in-game icon after 2 clicks
        patched.image_processor.locate_center_and_move.side_effect = [ValueError, ValueError, (10, 10)]
        patched.image_processor.locate_center.side_effect = [ValueError, ValueError, (0, 0)]
        picker = no_wait_picker()

        picker.pick_team(IMAGES)

        patched.get_monitor_id.assert_called_once_with(1234)
        assert patched.image_processor.load_needle_image.call_args_list == [mock.call("menu.png"), mock.call("ingame.png")]
        assert patched.image_processor.locate_center_and_move.call_count == 3
        assert patched.image_processor.locate_center.call_count == 3
        assert patched.click.call_count == 2
        picker._stop_event.wait.assert_any_call(15)
        patched.title.show_title.assert_called_once()

    def test_passes_monitor_and_region_offsets(self, patched):
        patched.get_monitor_id.return_value = 2
        patched.image_processor.locate_center_and_move.return_value = (10, 10)
        patched.image_processor.locate_center.return_value = (0, 0)

        no_wait_picker().pick_team(IMAGES)

        kwargs = patched.image_processor.locate_center_and_move.call_args.kwargs
        assert kwargs["monitor_xy"] == (1920, 0)
        assert kwargs["region_xy"] == (720, 400)
        assert kwargs["threshold"] == 0.9

    def test_stop_before_team_found(self, patched):
        patched.image_processor.locate_center_and_move.side_effect = ValueError
        picker = Picker()
        picker.stop()

        picker.pick_team(IMAGES)

        patched.screen_capture.capture_screen.assert_not_called()
        patched.click.assert_not_called()

    def test_stop_while_clicking(self, patched):
        patched.image_processor.locate_center_and_move.return_value = (10, 10)
        patched.image_processor.locate_center.side_effect = ValueError
        picker = Picker()
        # stop as soon as the first click happens
        patched.click.side_effect = picker.stop

        picker.pick_team(IMAGES)

        patched.click.assert_called_once()
        patched.title.show_title.assert_not_called()


class TestThreading:

    def test_start_runs_pick_on_background_thread(self):
        picker = Picker()
        ran_on = []
        done = threading.Event()

        def fake_pick(images):
            ran_on.append(threading.current_thread())
            done.set()

        with mock.patch.object(picker, "pick_team", side_effect=fake_pick):
            picker.start(IMAGES)
            assert done.wait(2)

        assert ran_on[0] is not threading.main_thread()
        assert ran_on[0].daemon

    def test_start_ignored_while_pick_running(self):
        picker = Picker()
        release = threading.Event()

        with mock.patch.object(picker, "pick_team", side_effect=lambda images: release.wait(2)) as pick_team:
            picker.start(IMAGES)
            first_thread = picker._thread
            picker.start(IMAGES)
            assert picker._thread is first_thread
            release.set()
            first_thread.join(2)

        pick_team.assert_called_once()

    def test_start_allowed_again_after_pick_finished(self):
        picker = Picker()

        with mock.patch.object(picker, "pick_team") as pick_team:
            picker.start(IMAGES)
            picker._thread.join(2)
            picker.start(IMAGES)
            picker._thread.join(2)

        assert pick_team.call_count == 2

    def test_stop_ends_running_pick_quickly(self, patched):
        patched.image_processor.locate_center_and_move.side_effect = ValueError
        picker = Picker()

        picker.start(IMAGES)
        picker.stop()
        picker._thread.join(2)

        assert not picker._thread.is_alive()

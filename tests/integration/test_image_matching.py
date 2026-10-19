"""
Runs the real team images through the real OpenCV matching, at the region sizes and thresholds picker.py uses.
"""
from unittest import mock

import pytest

from teams import Teams
from tests.conftest import make_haystack, make_noise
from utils.image_processor import ImageProcessor
from utils.utils import Utils

pytestmark = pytest.mark.integration

TEAMS = list(Teams)
# thresholds used in picker.py
MENU_THRESHOLD = 0.9
INGAME_THRESHOLD = 0.6


@pytest.mark.parametrize("team", TEAMS, ids=lambda team: team.name)
def test_team_images_load(team):
    for path in team.value:
        image = ImageProcessor.load_needle_image(path)
        assert image.ndim == 3 and image.shape[2] == 3


@pytest.mark.parametrize("team", TEAMS, ids=lambda team: team.name)
def test_menu_image_found_in_menu_region(team):
    needle = ImageProcessor.load_needle_image(team.value[0])
    _, _, width, height = Utils(None, 1920, 1080).scale_region()
    haystack = make_haystack(needle, width, height, x=150, y=90)

    with mock.patch.object(Utils, "move_mouse_to_position") as move_mouse:
        location = ImageProcessor.locate_center_and_move(haystack, needle, threshold=MENU_THRESHOLD)

    assert location == (150, 90)
    move_mouse.assert_called_once()


@pytest.mark.parametrize("team", TEAMS, ids=lambda team: team.name)
def test_ingame_image_found_in_ingame_region(team):
    needle = ImageProcessor.load_needle_image(team.value[1])
    _, _, width, height = Utils(None, 1920, 1080).scale_region_ingame()
    haystack = make_haystack(needle, width, height, x=5, y=8)

    assert ImageProcessor.locate_center(haystack, needle, threshold=INGAME_THRESHOLD) == (5, 8)


@pytest.mark.parametrize("team", TEAMS, ids=lambda team: team.name)
def test_ingame_image_fits_ingame_region_at_lowest_supported_resolution(team):
    needle = ImageProcessor.load_needle_image(team.value[1])
    _, _, width, height = Utils(None, 1280, 720).scale_region_ingame()
    assert needle.shape[0] <= height and needle.shape[1] <= width


@pytest.mark.parametrize("team", TEAMS, ids=lambda team: team.name)
def test_menu_image_not_found_in_noise(team):
    needle = ImageProcessor.load_needle_image(team.value[0])
    _, _, width, height = Utils(None, 1920, 1080).scale_region()

    with mock.patch.object(Utils, "move_mouse_to_position") as move_mouse:
        with pytest.raises(ValueError):
            ImageProcessor.locate_center_and_move(make_noise(width, height), needle, threshold=MENU_THRESHOLD)

    move_mouse.assert_not_called()


@pytest.mark.parametrize("picked, shown", [(a, b) for a in TEAMS for b in TEAMS if a is not b], ids=lambda team: team.name)
def test_picking_one_team_does_not_match_another_teams_button(picked, shown):
    needle = ImageProcessor.load_needle_image(picked.value[0])
    other_button = ImageProcessor.load_needle_image(shown.value[0])
    _, _, width, height = Utils(None, 1920, 1080).scale_region()
    haystack = make_haystack(other_button, width, height, x=150, y=90)

    with mock.patch.object(Utils, "move_mouse_to_position"):
        with pytest.raises(ValueError):
            ImageProcessor.locate_center_and_move(haystack, needle, threshold=MENU_THRESHOLD)

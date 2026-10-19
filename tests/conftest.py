"""
Shared fixtures for the unit and integration tests.
"""
import os

import numpy as np
import pytest

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(autouse=True)
def run_from_project_root(monkeypatch):
    # the team image paths in Teams are relative to the project root
    monkeypatch.chdir(PROJECT_ROOT)


def make_haystack(needle: np.ndarray, width: int, height: int, x: int, y: int, seed: int = 0) -> np.ndarray:
    """Build a BGRA noise image (the format mss returns) with the needle pasted at (x, y)."""

    rng = np.random.default_rng(seed)
    haystack = rng.integers(0, 256, size=(height, width, 4), dtype=np.uint8)
    haystack[..., 3] = 255
    needle_height, needle_width = needle.shape[:2]
    haystack[y:y + needle_height, x:x + needle_width, :3] = needle[..., :3]
    return haystack


def make_noise(width: int, height: int, seed: int = 1) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.integers(0, 256, size=(height, width, 4), dtype=np.uint8)


class FakeMSS:
    """Minimal stand-in for mss.MSS that records the regions it was asked to grab."""

    def __init__(self, monitors, frame=None):
        self.monitors = monitors
        self.frame = frame
        self.grabbed = []

    def grab(self, monitor):
        self.grabbed.append(monitor)
        if self.frame is not None:
            return self.frame
        return np.zeros((monitor["height"], monitor["width"], 4), dtype=np.uint8)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


@pytest.fixture
def fake_monitors():
    return [
        {"left": 0, "top": 0, "width": 3840, "height": 1080},
        {"left": 0, "top": 0, "width": 1920, "height": 1080},
        {"left": 1920, "top": 0, "width": 1920, "height": 1080},
    ]

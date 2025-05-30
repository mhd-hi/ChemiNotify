import os
import time
import win32gui
import win32con

from utils.popup_detector import PopupDetector
from .base import AppState
from .state_types import StateType
from utils.constants.texts import (
    EXEMPTED_WINDOW_TITLES,
    UNWANTED_WINDOW_TITLES,
    WINDOW_TITLES,
)


class InitialState(AppState):
    """Initial state - starts fresh by closing any unwanted windows and launching the app"""

    def detect(self) -> bool:
        # Always start here
        return True

    def _cleanup_unwanted_windows(self):
        """
        Close any visible windows containing specified substrings, except exempted ones.
        """

        popup_detector = PopupDetector()
        popup_detector.detect_and_handle_active_popups()

        def _close_if_unwanted(hwnd, _):
            if not win32gui.IsWindowVisible(hwnd):
                return
            title = win32gui.GetWindowText(hwnd) or ""
            lower = title.lower()

            to_remove = any(sub in lower for sub in UNWANTED_WINDOW_TITLES)
            to_exempt = any(ex in lower for ex in EXEMPTED_WINDOW_TITLES)

            if to_remove and not to_exempt:
                self.logger.info(f"Closing window: '{title}'")
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

        win32gui.EnumWindows(_close_if_unwanted, None)
        time.sleep(1)

    def handle(self) -> StateType:
        self.logger.info("InitialState: cleaning up unwanted windows...")

        # Perform cleanup of leftovers and popups
        self._cleanup_unwanted_windows()

        # Launch the JNLP application using environment variable
        jnlp_path = os.getenv("JNLP_PATH")
        if not jnlp_path:
            self.logger.error("Environment variable JNLP_PATH is not set")
            raise RuntimeError("Missing JNLP_PATH environment variable")

        self.logger.info(f"Starting JNLP application from: {jnlp_path}")
        os.startfile(jnlp_path)

        # Wait for the app to load
        self.logger.info("Waiting for Java to launch the application (3 seconds)...")
        time.sleep(3)

        # Focus the newly opened window
        app_titles = WINDOW_TITLES["LOGIN_TITLE_BAR"]
        self.logger.info("Attempting to locate and focus the Cheminot window...")
        window = self.ensure_window_focus(app_titles)
        if window:
            self.logger.info(f"Application window found: {window.title}")
            return StateType.LOGIN
        else:
            self.logger.error("Could not find application window after launch!")
            raise RuntimeError(
                "Failed to find and focus the Cheminot application window. "
                "Please check if the application launched correctly."
            )

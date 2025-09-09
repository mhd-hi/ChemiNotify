import time
from .base import AppState
from .state_types import StateType
from commands.coords import click
import pyautogui
from utils.constants.button_coords import TABS
from utils.constants.texts import WINDOW_TITLES


class ExitState(AppState):
    def detect(self) -> bool:
        return False

    def handle(self) -> StateType:
        self.logger.info("ExitState: starting clean-up...")

        time.sleep(4)
        window = self.ensure_window_focus(WINDOW_TITLES["MAIN_WINDOW"])
        if not window:
            self.logger.warning("Could not focus main window for quitting")
        else:
            quitter_coords = TABS["QUITTER"]
            self.logger.debug(f"Clicking 'QUIT' at {quitter_coords}")
            click(quitter_coords)
            time.sleep(1)

        login_window = self.ensure_window_focus(WINDOW_TITLES["LOGIN_TITLE_BAR"])
        if login_window:
            self.logger.debug("Login window detected. Sending Alt+F4 to close it")
            pyautogui.hotkey("alt", "f4")
            time.sleep(1)
        else:
            self.logger.warning("Login window not found; skipping Alt+F4")

        self.logger.info("ExitState: done, terminating state machine")
        return StateType.EXIT

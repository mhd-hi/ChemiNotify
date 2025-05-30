import time
import pygetwindow as gw

from .base import AppState
from .state_types import StateType
from utils.constants.button_coords import COLORS, TABS
from utils.coords import click, is_pixel_color_match
from utils.popup_detector import PopupDetector


class InscriptionState(AppState):
    def detect(self) -> bool:
        window = self.ensure_window_focus(["Le ChemiNot"])
        if not window:
            return False

        return is_pixel_color_match(
            window=window,
            coords=TABS["INSCRIPTION_SESSION"],
            element_name="INSCRIPTION_SESSION_TAB",
            expected_colors=COLORS["INSCRIPTION_SESSION"],
            logger=self.logger if hasattr(self, "logger") else None,
            tolerance=20,
        )

    def handle(self) -> StateType:
        """Handle the inscription state"""
        self.logger.info("Handling inscription state")

        window = self.ensure_window_focus(["Le ChemiNot"])
        if not window:
            self.logger.error(
                "Could not focus inscription window, attempting to continue"
            )

        # Initialize popup detector
        popup_detector = PopupDetector()

        # Click on SELECTION_COURS tab and handle any popups
        self.logger.info("Clicking on SELECTION_COURS tab")
        selection_coords = TABS["SELECTION_COURS"]

        popup_detector.detect_popup(
            action=lambda: click(selection_coords),
            timeout=1.0,
            handle_automatically=True,
        )

        # Ensure we check for any remaining popups before proceeding
        popup_detector.detect_and_handle_active_popups()

        time.sleep(1)

        self.logger.info(
            "Navigated to course selection, transitioning to selection course state"
        )
        return StateType.SELECTION_COURS

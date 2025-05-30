import time

from .base import AppState
from .state_types import StateType
from utils.coords import click, is_pixel_color_match
from utils.constants.button_coords import TABS, COLORS


class ConsultationState(AppState):
    def detect(self) -> bool:
        consultation_window = self.ensure_window_focus(["Le ChemiNot"])
        if not consultation_window:
            return False

        tab_coords = TABS["CONSULTATION"]
        active_colors = COLORS["CONSULTATION"]

        tab_is_active = is_pixel_color_match(
            window=consultation_window,
            coords=tab_coords,
            element_name="CONSULTATION_TAB",
            expected_colors=active_colors
        )

        if tab_is_active:
            self.logger.info("Consultation state detected - consultation tab is active")
            return True
        else:
            self.logger.info(
                "Consultation window found but consultation tab is not active"
            )
            return False

    def handle(self) -> StateType:
        self.logger.info("Handling consultation state")

        window = self.ensure_window_focus(["Le ChemiNot"])

        if not window:
            self.logger.warning(
                "Could not focus consultation window, attempting to continue"
            )

        self.logger.info("Clicking on INSCRIPTION_SESSION tab")
        click(TABS["INSCRIPTION_SESSION"], window=window)

        time.sleep(0.5)

        self.logger.info(
            "Navigated to inscription session, transitioning to inscription state"
        )
        return StateType.INSCRIPTION

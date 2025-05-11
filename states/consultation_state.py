import time
import pygetwindow as gw

from .base import AppState
from utils.coords import click
from utils.constants.button_coords import TABS

class ConsultationState(AppState):
    """Handles the main consultation screen after login"""
    
    def detect(self) -> bool:
        consultation_windows = gw.getWindowsWithTitle("CONSULTATION")
        if consultation_windows:
            self.logger.info("Consultation state detected via 'CONSULTATION' in title")
            return True
        # TODO: Double-check the color of the tab
        self.logger.info("Consultation state not detected")
        return False

    def handle(self) -> str:
        self.logger.info("Handling consultation state")
        
        # Ensure window focus
        window = self.ensure_window_focus(["CONSULTATION", "ChemiNot", "Cheminot"])
        if not window:
            self.logger.warning("Could not focus consultation window, attempting to continue")
        
        # Click on the INSCRIPTION_SESSION tab
        self.logger.info("Clicking on INSCRIPTION_SESSION tab")
        click(TABS['INSCRIPTION_SESSION'], window=window)

        time.sleep(0.5)
        
        self.logger.info("Navigated to inscription session, transitioning to inscription state")
        return "INSCRIPTION"
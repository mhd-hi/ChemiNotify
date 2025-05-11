import time
import pygetwindow as gw

from .base import AppState
from utils.constants.button_coords import TABS
from utils.coords import click

class InscriptionState(AppState):
    """Handles the inscription session screen"""
    
    def detect(self) -> bool:
        """Check if we're on the inscription screen"""
        # The inscription screen would still have CONSULTATION in the title
        consultation_windows = gw.getWindowsWithTitle("CONSULTATION")
        if not consultation_windows:
            return False

        # TODO: Double-check the color of the tab
        return True
    
    def handle(self) -> str:
        """Handle the inscription state"""
        self.logger.info("Handling inscription state")
        
        window = self.ensure_window_focus(["CONSULTATION", "ChemiNot", "Cheminot"])
        if not window:
            self.logger.error("Could not focus inscription window, attempting to continue")
        
        self.logger.info("Clicking on SELECTION_COURS tab")
        selection_coords = TABS['SELECTION_COURS']
        click(selection_coords)

        time.sleep(1)
        
        self.logger.info("Navigated to course selection, transitioning to selection course state")
        return "SELECTION_COURS"
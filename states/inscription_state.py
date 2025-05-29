import time
import pygetwindow as gw

from .base import AppState
from utils.constants.button_coords import TABS
from utils.coords import click
from utils.popup_detector import PopupDetector

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
        
        # Initialize popup detector
        popup_detector = PopupDetector()
        
        # Click on SELECTION_COURS tab and handle any popups
        self.logger.info("Clicking on SELECTION_COURS tab")
        selection_coords = TABS['SELECTION_COURS']
        
        popup_detector.detect_popup(
            action=lambda: click(selection_coords),
            timeout=1.0,
            handle_automatically=True
        )
        
        # Ensure we check for any remaining popups before proceeding
        popup_detector.detect_and_handle_active_popups()
        
        time.sleep(1)
        
        self.logger.info("Navigated to course selection, transitioning to selection course state")
        return "SELECTION_COURS"
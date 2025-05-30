import os
import pygetwindow as gw
import time
from typing import Optional, List, Union

from utils.logging_config import configure_logging
from utils.screenshot import screenshot, take_debug_screenshot

class AppState:
    """Base class for all application states."""
    
    def __init__(self):
        self.logger = configure_logging(self.__class__.__name__)

    def detect(self) -> bool:
        """
        Detect if the application is currently in this state
        Returns True if the current screen matches this state
        """
        self.logger.warning("Detect method not implemented in AppState base class")
        return False

    def handle(self) -> str:
        """
        Handle the current state and return the next state name
        """
        self.logger.warning("Handle method not implemented in AppState base class")
        return "EXIT"

    def is_debug_mode(self) -> bool:
        """Check if we're running in debug mode"""
        return os.getenv('LOG_LEVEL', '').upper() == 'DEBUG'
    
    def take_screenshot(self, name_suffix: Optional[str] = None) -> Optional[str]:
        """
        Takes a screenshot if in debug mode
        Returns path to screenshot file or None if not in debug mode
        """
        if not self.is_debug_mode():
            return None
            
        try:
            state_name = self.__class__.__name__.replace("State", "")
            name = f"{state_name}"
            if name_suffix:
                name = f"{name}_{name_suffix}"

            return take_debug_screenshot(name) # type: ignore
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {str(e)}")
            return None
    
    def take_error_screenshot(self, error_name: str = "error") -> Optional[str]:
        """Special version for error conditions"""
        return self.take_screenshot(f"ERROR_{error_name}")
    
    def ensure_window_focus(self, window_titles: List[str]) -> Optional[gw.Win32Window]:
        """
        Ensure the application window has focus.
        Match if window title startswith or contains the expected string, case-insensitive.
        """
        self.logger.debug("Ensuring window focus...")
        found_window = None

        # Get all window titles and log them (for debugging)
        windows = gw.getAllWindows()
        all_titles = [win.title for win in windows]
        self.logger.info(f"Current windows: {set(all_titles)}")

        for title in window_titles:
            self.logger.debug(f"Searching for window with title like '{title}'")
            for win in windows:
                # Use 'in' or startswith for fuzzy matching
                if self.normalize(title) in self.normalize(win.title): # type: ignore
                    found_window = win
                    self.logger.debug(f"Found window with fuzzy match '{win.title}'")
                    break
            if found_window:
                break

        if found_window:
            self.logger.debug("Found window, activating...")
            found_window.activate()
            time.sleep(0.1)
            return found_window

        self.take_error_screenshot("window_focus_failed")
        self.logger.warning("Could not find application window")
        return None

    @staticmethod
    def normalize(txt: str) -> str:
        """
        Normalize text for window matching: lower, ascii, strip, collapse whitespace.
        """
        import unicodedata, re
        if not txt:
            return ''
        txt = unicodedata.normalize('NFD', txt)
        txt = txt.encode('ascii', 'ignore').decode('utf-8')
        txt = re.sub(r'\s+', ' ', txt)
        return txt.lower().strip()
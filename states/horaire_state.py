import os
import time
import pygetwindow as gw

from .base import AppState
from notifications.discord import DiscordNotification
from utils.coords import moveTo, pixel, click
from utils.constants.button_coords import HORAIRE_STATE_COORDS, TABS
from utils.screenshot import screenshot

class HoraireState(AppState):
    """Handles the schedule/horaire view screen"""

    def detect(self) -> bool:
        return bool(gw.getWindowsWithTitle("CONSULTATION"))  # TODO: Double-check the color of the tab

    def _schedule_retry(self, minutes: float) -> str:
        """Helper to log, switch tab, sleep, and return to course selection."""
        wait_secs = minutes * 60
        next_run = time.strftime("%H:%M:%S", time.localtime(time.time() + wait_secs))
        self.logger.info(f"Will retry in {minutes}m (next at {next_run})")
        click(TABS['SELECTION_COURS'])
        time.sleep(1)
        time.sleep(wait_secs)
        return "SELECTION_COURS"

    def _take_window_screenshot(self, window, name_suffix=None) -> str | None:
        """
        Takes a screenshot of just the Cheminot window instead of the entire screen
        
        Args:
            window: The window object to capture
            name_suffix: Optional suffix to add to the filename
            
        Returns:
            Path to the saved screenshot or None
        """
        if not self.is_debug_mode():
            return None
            
        try:
            state_name = self.__class__.__name__.replace("State", "")
            name = f"{state_name}"
            if name_suffix:
                name = f"{name}_{name_suffix}"
                
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename = f"{timestamp}_{name}.png"
            filepath = os.path.join("logs/screenshots", filename)
            
            # Ensure directory exists
            os.makedirs("logs/screenshots", exist_ok=True)
            
            import win32gui
            hwnd = window._hWnd
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            width, height = right - left, bottom - top
            
            img = screenshot(region=(0, 0, width, height), window=window)
            img.save(filepath)
            
            self.logger.debug(f"Window screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"Error taking window screenshot: {str(e)}")
            return None

    def handle(self) -> str:
        self.logger.info("Handling HoraireState: checking course availability")

        window = self.ensure_window_focus(["CONSULTATION", "ChemiNot", "Cheminot"])
        if not window:
            self.logger.warning("Could not focus horaire window, but continuing")
            self.take_error_screenshot("no_window_found")

        # Take screenshot
        screenshot_path = self._take_window_screenshot(window, "before_pixel_check")

        logical_pt = HORAIRE_STATE_COORDS['GROUP_COURSE_BLACK_PIXEL']
        moveTo(logical_pt, window=window, duration=0.1)
        time.sleep(0.1)

        try:
            r, g, b = pixel(logical_pt, window=window)
        except Exception as e:
            self.logger.error(f"Error accessing pixel: {e}")
            self.take_error_screenshot("pixel_check_failed")
            return "EXIT"

        course_code = os.getenv('TRACKING_COURSE_CODE', 'GTI611').upper()
        base_retry_min = float(os.getenv('COURSE_NOT_AVAILABLE_RETRY_WAIT_MINUTES', 10))

        if (r, g, b) == (0, 0, 0): 
            # BLACK pixel means course is available
            self.logger.info(f"{course_code} is available (pixel is black) - sending notification")
            
            current_time = time.strftime("%B %d, %Y at %I:%M %p")
            subject = "Course available"
            body = f"{course_code} is now available!\n"
            body += f"Detected on {current_time}"
            
            discord_notifier = DiscordNotification()
            discord_notifier.send(subject, body, screenshot_path)
            return self._schedule_retry(base_retry_min * 2)
        elif (r, g, b) == (192, 192, 192):
            # NOT available - retry after base interval
            self.logger.info(f"{course_code} not available (pixel is gray C0C0C0) - retrying in {base_retry_min}m")
            return self._schedule_retry(base_retry_min)
        else:
            discord_notifier = DiscordNotification()
            discord_notifier.send("ERROR: unexpected_pixel_color", 
                                  "RGB: " + str((r, g, b)), 
                                  screenshot_path)
            self.logger.error(f"Unexpected pixel color: RGB({r}, {g}, {b})")
            # Still retry after normal interval to keep the program running
            self.logger.info(f"Continuing with normal retry interval of {base_retry_min}m")
            return self._schedule_retry(base_retry_min)
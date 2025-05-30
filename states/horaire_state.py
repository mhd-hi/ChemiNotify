import os
import time

from .base import AppState
from .state_types import StateType
from notifications.discord import DiscordNotification
from utils.coords import moveTo, pixel, click, is_pixel_color_match
from utils.constants.button_coords import COLORS, HORAIRE_STATE_COORDS, TABS
from utils.screenshot import screenshot
from utils.file_utils import save_file

class HoraireState(AppState):
    def detect(self) -> bool:
        window = self.ensure_window_focus(["Le ChemiNot"])
        if not window:
            return False
        
        return is_pixel_color_match(
            window=window,
            coords=TABS['HORAIRE'],
            element_name="HORAIRE_TAB",
            expected_colors=COLORS['HORAIRE'],
            logger=self.logger if hasattr(self, 'logger') else None,
            tolerance=20
        )

    def _schedule_retry(self, minutes: float) -> StateType:
        """Helper to log, switch tab, sleep, and return to course selection."""
        wait_secs = minutes * 60
        next_run = time.strftime("%H:%M:%S", time.localtime(time.time() + wait_secs))
        self.logger.info(f"Will retry in {minutes}m (next at {next_run})")
        click(TABS['SELECTION_COURS'])
        time.sleep(1)
        time.sleep(wait_secs)
        return StateType.SELECTION_COURS

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
            import win32gui
            
            state_name = self.__class__.__name__.replace("State", "")
            
            hwnd = window._hWnd
            left, top, right, bottom = win32gui.GetClientRect(hwnd)
            width, height = right - left, bottom - top
            
            img = screenshot(region=(0, 0, width, height), window=window)
            return save_file(img, state_name, suffix=name_suffix)
        except Exception as e:
            self.logger.error(f"Error taking window screenshot: {str(e)}")
            return None

    def handle(self) -> StateType:
        self.logger.info("Handling HoraireState: checking course availability")

        window = self.ensure_window_focus(["Le ChemiNot"])
        if not window:
            self.logger.warning("Could not focus horaire window, but continuing")
            self.take_error_screenshot("no_window_found")

        screenshot_path = self._take_window_screenshot(window, "before_pixel_check")

        logical_pt = HORAIRE_STATE_COORDS['GROUP_COURSE_BLACK_PIXEL']
        moveTo(logical_pt, window=window, duration=0.1)
        time.sleep(0.1)

        course_code = os.getenv('TRACKING_COURSE_CODE', 'GTI611').upper()
        base_retry_min = float(os.getenv('COURSE_NOT_AVAILABLE_RETRY_WAIT_MINUTES', 10))

        # Check if course is available using is_pixel_color_match with colors from COLORS constant
        if is_pixel_color_match(
            window=window, 
            coords=logical_pt, 
            element_name="COURSE_AVAILABLE", 
            expected_colors=COLORS['COURSE_AVAILABLE'],
            logger=self.logger,
            tolerance=10
        ):
            # BLACK pixel means course is available
            self.logger.info(f"{course_code} is available (pixel is black) - sending notification")
            
            current_time = time.strftime("%B %d, %Y at %I:%M %p")
            subject = "Course available"
            body = f"{course_code} is now available!\n"
            body += f"Detected on {current_time}"
            
            discord_notifier = DiscordNotification()
            discord_notifier.send(subject, body, screenshot_path)
            return self._schedule_retry(base_retry_min * 2)
        elif is_pixel_color_match(
            window=window, 
            coords=logical_pt, 
            element_name="COURSE_UNAVAILABLE", 
            expected_colors=COLORS['COURSE_UNAVAILABLE'],
            logger=self.logger,
            tolerance=15  # Slightly higher tolerance for gray
        ):
            # NOT available - retry after base interval
            self.logger.info(f"{course_code} not available (pixel is gray C0C0C0) - retrying in {base_retry_min}m")
            return self._schedule_retry(base_retry_min)
        else:
            # Unexpected color - get the actual color for the error message
            try:
                r, g, b = pixel(logical_pt, window=window)
                discord_notifier = DiscordNotification()
                discord_notifier.send("ERROR: unexpected_pixel_color", 
                                    "RGB: " + str((r, g, b)), 
                                    screenshot_path)
                self.logger.error(f"Unexpected pixel color: RGB({r}, {g}, {b})")
            except Exception as e:
                self.logger.error(f"Error accessing pixel: {e}")
                self.take_error_screenshot("pixel_check_failed")
                
            self.logger.info(f"Continuing with normal retry interval of {base_retry_min}m")
            return self._schedule_retry(base_retry_min)
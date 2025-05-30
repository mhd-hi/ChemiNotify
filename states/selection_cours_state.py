import os
import time
import pygetwindow as gw
import pytesseract
import pyautogui

from .base import AppState
from .state_types import StateType
from utils.constants.button_coords import COLORS, COURSE_SELECTION_COORDS, TABS
from utils.window_helpers import list_window_titles, wait_for_new_window
from utils.coords import click, is_pixel_color_match
from utils.screenshot import screenshot

class SelectionCoursState(AppState):
    def detect(self) -> bool:
        """
        Detects if the current state is the Selection Cours state by checking:
        1. If the 'Le ChemiNot' window exists
        2. If the Selection Cours tab has the expected color indicating it's active
        """
        window = self.ensure_window_focus(["Le ChemiNot"])
        if not window:
            return False
        
        return is_pixel_color_match(
            window=window,
            coords=TABS['SELECTION_COURS'],
            element_name="SELECTION_COURS_TAB",
            expected_colors=COLORS['SELECTION_COURS'],
            logger=self.logger if hasattr(self, 'logger') else None,
            tolerance=20
        )

    def handle(self) -> StateType:
        self.logger.info("Handling course selection state")

        window = self.ensure_window_focus(["Le ChemiNot"])
        if not window:
            self.logger.warning("Could not focus course selection window")

        self.logger.info("Switching to SELECTION_COURS tab")
        click(TABS['SELECTION_COURS'])
        time.sleep(1)

        course_code = os.getenv('TRACKING_COURSE_CODE', 'GTI611')
        if course_code:
            course_code = course_code.upper()
        else:
            self.logger.error("TRACKING_COURSE_CODE environment variable not set, using default")
            course_code = 'GTI611'

        # Coordinates of the course button
        coords = COURSE_SELECTION_COORDS.get(course_code)
        if not coords:
            self.logger.error(f"No coordinates for course {course_code}, exiting.")
            return StateType.EXIT

        before = list_window_titles()
        click(coords)

        # Fix for window.title in ignore set
        ignore_set = {"CONSULTATION"}
        if window:
            ignore_set.add(window.title)

        new_title = wait_for_new_window(
            before,
            timeout=1.5,
            ignore=ignore_set
        )

        if new_title:
            self.logger.info(f"-> Detected popup: '{new_title}'")
            popup = gw.getWindowsWithTitle(new_title)[0]
            popup.activate()
            time.sleep(0.3)

            # OCR the popup text
            bbox = (popup.left, popup.top, popup.width, popup.height)
            img = screenshot(region=bbox)
            text = pytesseract.image_to_string(img).lower()
            self.logger.debug(f"Popup text: {repr(text)}")

            try:
                popup.close()
                self.logger.info("-> Closed popup window cleanly")
            except Exception:
                pyautogui.hotkey('alt', 'f4')
                self.logger.info("-> Closed popup window with Alt+F4")

            # If course is full, wait and retry
            if "complets" in text or "annulations" in text:
                retry_wait_min = float(os.getenv('COURSE_NOT_AVAILABLE_RETRY_WAIT_MINUTES', 10))
                wait_secs = retry_wait_min * 60

                self.logger.info(
                    f"Course full, retrying in {retry_wait_min}m (next at {time.strftime('%H:%M:%S', time.localtime(time.time() + wait_secs))})"
                )
                time.sleep(wait_secs)
                return StateType.SELECTION_COURS
            else:
                self.logger.warning("Popup was not a 'course full' message, proceeding.")

                self.take_screenshot("popup_debug")

        # No blocking popup or course open -> advance to availability check
        self.logger.info("No blocking popup; moving to availability check")
        return StateType.HORAIRE

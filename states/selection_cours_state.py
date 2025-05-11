import os
import time
import pygetwindow as gw
import pytesseract
import pyautogui

from .base import AppState
from utils.constants.button_coords import COURSE_SELECTION_COORDS, TABS
from utils.window_helpers import list_window_titles, wait_for_new_window
from utils.coords import click
from utils.screenshot import screenshot

class SelectionCoursState(AppState):
    def detect(self) -> bool:
        return bool(gw.getWindowsWithTitle("CONSULTATION"))

    def handle(self) -> str:
        self.logger.info("Handling course selection state")

        window = self.ensure_window_focus(["CONSULTATION", "ChemiNot", "Cheminot"])
        if not window:
            self.logger.warning("Could not focus course selection window")

        self.logger.info("Switching to SELECTION_COURS tab")
        click(TABS['SELECTION_COURS'])
        time.sleep(1)

        # Coordinates of the course button
        course_code = os.getenv('TRACKING_COURSE_CODE').upper()
        coords = COURSE_SELECTION_COORDS.get(course_code)
        if not coords:
            self.logger.error(f"No coordinates for course {course_code}, exiting.")
            return "EXIT"

        before = list_window_titles()
        click(coords)

        new_title = wait_for_new_window(
            before,
            timeout=1.5,
            ignore={window.title, "CONSULTATION"}
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
                retry_wait_min = float(os.getenv('COURSE_NOT_AVAILABLE_RETRY_WAIT_MINUTES'))
                wait_secs = retry_wait_min * 60

                self.logger.info(
                    f"Course full, retrying in {retry_wait_min}m (next at {time.strftime("%H:%M:%S", time.localtime(time.time() + wait_secs))})"
                )
                time.sleep(wait_secs)
                return "SELECTION_COURS"
            else:
                self.logger.warning("Popup was not a 'course full' message, proceeding.")

                self.take_screenshot("popup_debug")

        # No blocking popup or course open -> advance to availability check
        self.logger.info("No blocking popup; moving to availability check")
        return "HORAIRE"

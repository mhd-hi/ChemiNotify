import os
import time
import pyautogui
import pygetwindow as gw
from typing import Optional, Tuple, Set, Callable, Any

from utils.window_helpers import list_window_titles, wait_for_new_window
from commands.screenshot import screenshot
from utils.logging_config import configure_logging
from utils.constants.texts import POPUP_TYPES, POPUP_UNKNOWN_RETURN_VALUE


class PopupDetector:
    """Utility class for detecting and handling popup windows in the application."""

    def __init__(self):
        """
        Initialize popup detector.
        """
        self.logger = configure_logging("PopupDetector")

    def detect_popup(
        self,
        action: Callable[[], Any],
        timeout: float = 1.5,
        ignore_titles: Optional[Set[str]] = None,
        activate: bool = True,
        close_after: bool = False,
        handle_automatically: bool = True,
    ) -> Tuple[Optional[str], Optional[gw.Window], Optional[str]]:
        """
        Execute an action and detect if it causes a popup window to appear.

        Args:
            action: Function to execute (like clicking a button)
            timeout: How long to wait for popup
            ignore_titles: Window titles to ignore
            activate: Whether to activate the popup window if found
            close_after: Whether to close the popup after detection
            handle_automatically: Whether to automatically capture text and handle the popup

        Returns:
            Tuple of (popup_title, popup_window, popup_type)
            or (None, None, None) if no popup detected
        """
        ignore_titles = ignore_titles or set()

        # Get window titles before action
        before = list_window_titles()

        # Execute the action that might trigger a popup
        result = action()

        # Wait for a new window to appear
        new_title = wait_for_new_window(before, timeout=timeout, ignore=ignore_titles)

        # If we found a new window, return its title and window object
        if new_title:
            self.logger.info(f"Detected popup: '{new_title}'")
            try:
                popup_windows = gw.getWindowsWithTitle(new_title)
                if not popup_windows:
                    self.logger.warning(
                        f"Found popup title '{new_title}' but couldn't get window object"
                    )
                    return new_title, None, None

                popup_window = popup_windows[0]

                if activate:
                    popup_window.activate()
                    time.sleep(0.1)

                popup_type = None

                # If set to handle automatically, capture text and handle
                if handle_automatically:
                    self.logger.debug(
                        "Automatic popup handling enabled, capturing text..."
                    )
                    popup_text = self.capture_popup_text(popup_window)
                    if popup_text:
                        popup_type = self.handle_popups(
                            popup_window, popup_text, new_title
                        )
                        self.logger.debug(
                            f"Automatically handled popup as type: {popup_type}"
                        )
                        # The popup is already closed by handle_popups
                        return new_title, None, popup_type
                    else:
                        self.logger.debug(
                            "No text captured from popup, cannot handle automatically"
                        )
                elif close_after:
                    self.logger.debug(
                        "Automatic handling disabled, but close_after=True"
                    )
                    self.close_popup(popup_window)
                    return new_title, None, None

                return new_title, popup_window, popup_type

            except IndexError:
                self.logger.warning(
                    f"Found popup title '{new_title}' but window disappeared"
                )
                return new_title, None, None

        return None, None, None

    def capture_popup_text(self, popup_window: gw.Window) -> Optional[str]:
        """
        Capture text content from a popup window using OCR.
        Requires pytesseract to be properly configured.
        """
        try:
            import pytesseract
            from utils.file_utils import save_file

            if popup_window is None:
                self.logger.error("Cannot capture text from None window")
                return None

            window_info = f"{popup_window.title if hasattr(popup_window, 'title') else 'Unknown'} ({popup_window.width}x{popup_window.height})"
            self.logger.debug(f"Capturing text from popup window: {window_info}")

            time.sleep(0.2)

            # Take screenshot of popup
            self.logger.debug("Taking screenshot of popup window")
            region = (
                popup_window.left,
                popup_window.top,
                popup_window.width,
                popup_window.height,
            )
            popup_img = screenshot(region=region)

            if popup_img is None:
                self.logger.error("Failed to capture popup screenshot")
                return None

            # Extract text with OCR
            self.logger.debug("Starting OCR text extraction")
            text = pytesseract.image_to_string(popup_img, lang="fra")

            trimmed_text = text.strip() if text else ""

            # Check if popup is recognized
            popup_recognized = self.is_popup_recognized(popup_window, trimmed_text)

            # Save the screenshot only for unrecognized popups
            if not popup_recognized:
                window_title = (
                    popup_window.title if hasattr(popup_window, "title") else "unknown"
                )
                # Sanitize filename
                window_title = "".join(
                    c if c.isalnum() or c in " -_" else "_" for c in window_title
                )

                # Use the save_file utility
                screenshot_path = save_file(
                    popup_img, window_title, directory="logs/ocr_screenshots"
                )
                self.logger.debug(
                    f"Saved unrecognized popup screenshot to: {screenshot_path}"
                )

            if trimmed_text:
                self.logger.debug(f"OCR extracted {len(trimmed_text)} characters")
                self.logger.debug(
                    f"OCR text sample: '{trimmed_text[:50]}{'...' if len(trimmed_text) > 50 else ''}'"
                )
                return trimmed_text
            else:
                self.logger.debug("OCR returned empty text")
                return None

        except Exception as e:
            self.logger.error(f"Failed to capture popup text: {e}")
            return None

    def handle_popups(self, popup_window, popup_text, popup_title=None):

        if popup_window is None:
            self.logger.debug("No popup window provided to handle_popups")
            return None

        self.logger.debug(
            f"Analyzing popup - Title: '{popup_title}', Text length: {len(popup_text) if popup_text else 0}"
        )

        norm_popup = normalize(popup_text) if popup_text else ""
        norm_title = normalize(popup_title) if popup_title else ""

        for popup_type in POPUP_TYPES:
            popup_name = popup_type.get("return_value", "unknown")
            # Title matching
            title_match = True
            if popup_type["title"] and popup_title:
                title_matches = [
                    title
                    for title in popup_type["title"]
                    if normalize(title) in norm_title
                ]
                title_match = len(title_matches) > 0
                self.logger.debug(
                    f"Title match result for {popup_name}: {title_match} (matched: {title_matches if title_match else 'none'})"
                )

            # Text matching
            text_match = True
            if popup_type["text"] and popup_text:
                text_matches = [
                    text for text in popup_type["text"] if normalize(text) in norm_popup
                ]
                text_match = len(text_matches) > 0
                self.logger.debug(
                    f"Text match result for {popup_name}: {text_match} (matched: {text_matches if text_match else 'none'})"
                )

            # If both title and text match their patterns, handle this popup type
            if title_match and text_match:
                return_value = popup_type["return_value"]
                self.logger.warning(f"Detected {return_value} popup")

                try:
                    if popup_type.get("action") == "click_ok":
                        self.logger.debug(
                            f"Handling {return_value} popup with OK button click"
                        )
                        self.click_ok_button(popup_window)
                    elif popup_type.get("action") == "alt_f4":
                        self.logger.debug(f"Handling {return_value} popup with Alt+F4")
                        self.close_popup(popup_window)
                    else:
                        self.logger.debug(
                            f"Handling {return_value} popup with standard close"
                        )
                        self.close_popup(popup_window)
                except Exception as e:
                    self.logger.error(f"Error handling popup: {e}", exc_info=True)
                return return_value

        self.logger.debug("No matching popup type found, handling as unknown popup")
        try:
            self.close_popup(popup_window)
        except Exception as e:
            self.logger.error(f"Error closing unknown popup: {e}", exc_info=True)
        return POPUP_UNKNOWN_RETURN_VALUE

    def close_popup(self, popup_window):
        """
        Safely close a popup window

        Args:
            popup_window: Window object to close
        """
        if popup_window is None:
            self.logger.debug("Cannot close None popup window")
            return

        self.logger.debug(
            f"Attempting to close popup window: {popup_window.title if hasattr(popup_window, 'title') else 'Unknown'}"
        )

        try:
            popup_window.close()
            self.logger.debug("Popup closed successfully with window.close()")
        except Exception as e:
            self.logger.warning(f"Could not close popup normally: {e}")
            self.logger.debug(f"Close failure details: {str(e)}")
            try:
                self.logger.debug("Attempting Alt+F4 method to close popup")
                popup_window.activate()
                time.sleep(0.1)
                pyautogui.hotkey("alt", "f4")
                self.logger.debug("Alt+F4 sent to popup window")
            except Exception as e2:
                self.logger.error(f"Failed to close popup with Alt+F4: {e2}")
                self.logger.debug(f"Alt+F4 failure details: {str(e2)}")

    def detect_and_handle_active_popups(self):
        """
        Detect and handle any currently active popups.
        """
        self.logger.debug("Scanning for active popups...")

        # Skip these window titles when looking for popups to handle
        skip_titles = {"Program Manager", "Windows Input Experience"}

        # Add critical application windows that should never be closed automatically
        protected_titles = {"Bienvenue sur ChemiNot", "Le ChemiNot"}

        for window in gw.getAllWindows():
            if not window.visible or not window.title.strip():
                continue

            window_title = window.title

            # Skip windows in the skip list
            if any(title in window_title for title in skip_titles):
                continue

            # Never close main application windows
            if any(title in window_title for title in protected_titles):
                self.logger.debug(f"Skipping protected window: '{window_title}'")
                continue

            # Check if this looks like a popup (by size)
            win_width, win_height = window.width, window.height
            self.logger.debug(
                f"Checking window: '{window_title}' ({win_width}x{win_height})"
            )

            if win_width > 800 or win_height > 600:
                self.logger.debug(
                    f"Skipping large window (window > 800): {win_width}x{win_height}"
                )
                continue

            # Only consider windows that look like popups
            if win_width < 800 and win_height < 600:
                # This is likely a popup, try to handle it
                self.logger.debug(
                    f"Found potential popup: '{window_title}' ({win_width}x{win_height})"
                )

                # For session selection popups, don't close them automatically
                if "ChemiNot" in window_title and "session" in window_title.lower():
                    self.logger.info(
                        f"Found session selection popup: '{window_title}', keeping open"
                    )
                    continue

                # Get popup text and determine popup type
                popup_text = self.capture_popup_text(window)
                popup_type = self.handle_popups(window, popup_text, window_title)

                if popup_type and popup_type != POPUP_UNKNOWN_RETURN_VALUE:
                    self.logger.info(
                        f"Successfully handled popup of type: {popup_type}"
                    )
                else:
                    # If we can't determine the type but it's small enough to be a popup,
                    # try to close it using the default method
                    self.logger.debug(
                        f"No matching popup type found, handling as unknown popup"
                    )
                    self.close_popup(window)

        self.logger.debug("Popup scanning and handling complete")

    def click_ok_button(self, popup_window):
        """
        Click the OK button on a popup using the image in assets/ok_button

        Args:
            popup_window: Window object containing the OK button
        """

        if popup_window is None:
            self.logger.debug("Cannot click OK on None popup window")
            return

        self.logger.debug(
            f"Attempting to click OK button on popup: {popup_window.title if hasattr(popup_window, 'title') else 'Unknown'}"
        )

        try:
            # Activate the window first
            popup_window.activate()
            time.sleep(
                0.5
            )  # Increased timeout to ensure window is fully active and rendered

            # Find and click the OK button using image recognition
            ok_button_path = os.path.join("assets", "ok_button.png")

            if not os.path.exists(ok_button_path):
                self.logger.error(f"OK button image not found at {ok_button_path}")
                self.close_popup(popup_window)  # Fallback to closing
                return

            self.logger.debug(f"Searching for OK button using image: {ok_button_path}")

            # Limit the search to the popup window
            region = (
                popup_window.left,
                popup_window.top,
                popup_window.width,
                popup_window.height,
            )

            # Try to locate the OK button on screen
            time.sleep(0.3)

            try:
                ok_location = pyautogui.locateOnScreen(
                    ok_button_path, confidence=0.7, region=region
                )
                if ok_location:
                    x, y = pyautogui.center(ok_location)
                    self.logger.debug(
                        f"Found OK button at {x}, {y} - moving mouse to hover"
                    )
                    # First hover over the button
                    pyautogui.moveTo(x, y)
                    time.sleep(0.5)  # Wait while hovering before clicking
                    self.logger.debug("Clicking OK button after hover")
                    pyautogui.click()
                    self.logger.info("Successfully clicked OK button")
                    time.sleep(0.5)  # Wait a moment after clicking
                    return
                else:
                    self.logger.warning("Could not find OK button on screen")
            except Exception as e:
                self.logger.error(f"Error looking for OK button: {e}")

            # If we got here, we couldn't find or click the OK button
            # Fall back to Enter key (which often confirms dialogs)
            self.logger.debug("Trying Enter key as fallback for OK")
            pyautogui.press("enter")
            time.sleep(0.3)

            # Check if popup is still active - if so, try Escape or Alt+F4
            if popup_window.isActive:
                self.logger.debug("Enter key didn't work, trying Alt+F4 fallback")
                self.close_popup(popup_window)

        except Exception as e:
            self.logger.error(f"Error handling OK button click: {e}")
            # Try to close the popup as a last resort
            self.close_popup(popup_window)

    def is_popup_recognized(self, popup_window, trimmed_text):
        """
        Check if a popup is recognized based on its title and text content.

        Args:
            popup_window: Window object to check
            trimmed_text: OCR extracted text from the popup

        Returns:
            bool: True if popup is recognized, False otherwise
        """
        norm_popup = normalize(trimmed_text) if trimmed_text else ""
        norm_title = (
            normalize(popup_window.title) if hasattr(popup_window, "title") else ""
        )

        for popup_type in POPUP_TYPES:
            # Title matching
            title_match = True
            if popup_type["title"] and hasattr(popup_window, "title"):
                title_matches = [
                    title
                    for title in popup_type["title"]
                    if normalize(title) in norm_title
                ]
                title_match = len(title_matches) > 0

            # Text matching
            text_match = True
            if popup_type["text"] and trimmed_text:
                text_matches = [
                    text for text in popup_type["text"] if normalize(text) in norm_popup
                ]
                text_match = len(text_matches) > 0

            # If both title and text match, this is a recognized popup
            if title_match and text_match:
                return True

        return False


def normalize(txt: str) -> str:
    """
    Normalize text for window matching: lower, ascii, strip, collapse whitespace.
    """
    import unicodedata, re

    txt = unicodedata.normalize("NFD", txt)
    txt = txt.encode("ascii", "ignore").decode("utf-8")
    txt = re.sub(r"\s+", " ", txt)
    return txt.lower().strip()

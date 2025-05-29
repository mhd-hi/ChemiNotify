import os
import time
import pyautogui
import pygetwindow as gw
import dotenv

from .base import AppState
from utils.coords import click
from utils.constants.button_coords import LOGIN_STATE_COORDS
from utils.constants.texts import WINDOW_TITLES
from utils.popup_detector import PopupDetector

class LoginState(AppState):    
    def detect(self) -> bool:
        for title in WINDOW_TITLES['LOGIN_TITLE_BAR']:
            if gw.getWindowsWithTitle(title):
                self.logger.info(f"Login state detected: found window with '{title}' title")
                return True

        self.logger.info("Login state not detected")
        return False

    def handle(self) -> str:
        self.logger.info("Handling login state")

        window = self.ensure_window_focus(WINDOW_TITLES['LOGIN_TITLE_BAR'])
        
        if not window:
            self.logger.warning("Could not focus login window, attempting login anyway")
        
        # Load environment variables
        dotenv.load_dotenv()

        app_username = os.getenv("CHEMINOT_USERNAME", "add me in .env file")
        if app_username:
            app_username = app_username.strip('"')
            
        app_password = os.getenv("CHEMINOT_PASSWORD", "add me in .env file")
        if app_password:
            app_password = app_password.strip('"')

        if not app_username or not app_password:
            self.logger.error("Missing credentials in .env file (CHEMINOT_USERNAME or CHEMINOT_PASSWORD)")
            return "ERROR"

        self.logger.info("Entering username...")
        click(LOGIN_STATE_COORDS['USERNAME_FIELD'], window=window, state_name="LOGIN")
        time.sleep(1.0)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.5)
        pyautogui.press('delete')
        time.sleep(0.7)

        for char in app_username:
            pyautogui.write(char)
            time.sleep(0.1)
        time.sleep(0.3)

        self.logger.info("Entering password...")
        click(LOGIN_STATE_COORDS['PASSWORD_FIELD'], window=window, state_name="LOGIN")
        time.sleep(0.1)
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        pyautogui.press('delete')
        time.sleep(0.3)

        for char in app_password:
            pyautogui.write(char)
            time.sleep(0.1)
            
        self.logger.info("Clicking login button...")
        time.sleep(0.5)
        click(LOGIN_STATE_COORDS['LOGIN_BUTTON'], window=window, state_name="LOGIN")

        self.logger.info("Waiting for login to complete (3 seconds)")
        time.sleep(2.0)

        # Check for and handle any popups that might be active
        detector = PopupDetector()
        detector.detect_and_handle_active_popups()

        self.logger.info("Login complete, transitioning to consultation state")
        return "CONSULTATION"
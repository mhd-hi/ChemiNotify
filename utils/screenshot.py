import os
import time
import logging
import pyautogui
import pygetwindow as gw
import win32gui

from utils.coords import _client_to_screen, _scale_for_window
from utils.constants.button_coords import REF_WINDOW_SIZES

logger = logging.getLogger(__name__)

def take_debug_screenshot(name: str, directory: str = "logs/screenshots") -> str: # TODO:  this should not be used
    """
    Takes a screenshot of the current screen and saves it with timestamp
    Only if LOG_LEVEL is set to DEBUG
    
    Args:
        name: Base name for the screenshot
        directory: Directory to save screenshots
    
    Returns:
        Path to the saved screenshot or None if not in DEBUG mode
    """
    if os.getenv('LOG_LEVEL', '').upper() != 'DEBUG':
        return None
        
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{timestamp}_{name}.png"
        filepath = os.path.join(directory, filename)
        
        take_screenshot = screenshot()
        take_screenshot.save(filepath)
        
        logger.debug(f"Debug screenshot saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error taking debug screenshot: {str(e)}")
        logger.error(f"Error screenshot saved: {filepath}")
        return None

def screenshot(region=None, window=None, state_name="LE_CHEMINOT"):
    """
    Take a screenshot.
        - If region=(x,y,w,h) in logical client coords and window is given (or active),
          crops that client region scaled for state_name.
        - If region only and no window, uses screen coords.
        - If neither, full screen.
    """
    if window is None and region:
        window = gw.getActiveWindow()

    # Case A: logical region + window to scale & crop
    if window and region:
        hwnd = window._hWnd
        x, y, w, h = region

        # 1) get the physical origin
        phys_x, phys_y = _scale_for_window(hwnd, (x, y), state_name)

        # 2) recompute sx, sy exactly as in coords._scale_for_window
        ref_w, ref_h = REF_WINDOW_SIZES[state_name]
        left, top, right, bottom = win32gui.GetClientRect(hwnd)
        actual_w, actual_h = right - left, bottom - top
        sx = actual_w / ref_w
        sy = actual_h / ref_h

        # 3) scale width/height
        phys_w = int(w * sx)
        phys_h = int(h * sy)

        # 4) map client to screen
        screen_x, screen_y = _client_to_screen(hwnd, (phys_x, phys_y))

        return pyautogui.screenshot(region=(screen_x, screen_y, phys_w, phys_h))
    # Case B: region only, no window context
    elif region:
        return pyautogui.screenshot(region=region)

    # Case C: full-screen
    else:
        return pyautogui.screenshot()


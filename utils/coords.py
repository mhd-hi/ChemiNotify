import time
import win32gui
import pyautogui
import pygetwindow as gw
from datetime import datetime
import os

from utils.constants.button_coords import REF_WINDOW_SIZES
from utils.logging_config import configure_logging
from utils.screenshot import screenshot

logger = configure_logging("Coords")


def _client_to_screen(hwnd, point):
    """Win32 ClientToScreen in physical px; returns (x,y) in physical px."""
    ox, oy = win32gui.ClientToScreen(hwnd, (0, 0))
    return ox + point[0], oy + point[1]


def _scale_for_window(hwnd, logical_point, state_name):
    """Turn a logical_point in your design coords into a physical client px tuple."""
    ref_sizes = REF_WINDOW_SIZES.get(state_name)
    if not ref_sizes:
        logger.error(
            f"State name '{state_name}' not found in REF_WINDOW_SIZES, using default size."
        )
        ref_w, ref_h = 1024, 768
    else:
        ref_w, ref_h = ref_sizes

    left, top, right, bottom = win32gui.GetClientRect(hwnd)
    actual_w, actual_h = right - left, bottom - top

    sx, sy = actual_w / ref_w, actual_h / ref_h
    phys_x = int(logical_point[0] * sx)
    phys_y = int(logical_point[1] * sy)
    return phys_x, phys_y


def click(logical_point, window=None, state_name="LE_CHEMINOT"):
    """
    Click at logical client-relative point inside `window` (default
    state_name="LE_CHEMINOT").  Uses REF_SIZES to scale.
    """
    if window is None:
        window = gw.getActiveWindow()

    if window:
        hwnd = window._hWnd
        phys_pt = _scale_for_window(hwnd, logical_point, state_name)
        screen_x, screen_y = _client_to_screen(hwnd, phys_pt)
    else:
        screen_x, screen_y = logical_point

    pyautogui.click(screen_x, screen_y)


def moveTo(logical_point, window=None, duration=0.0, state_name="LE_CHEMINOT"):
    """
    Move to logical client-relative point inside `window`.
    """
    if window is None:
        window = gw.getActiveWindow()

    if window:
        hwnd = window._hWnd
        phys_pt = _scale_for_window(hwnd, logical_point, state_name)
        screen_x, screen_y = _client_to_screen(hwnd, phys_pt)
    else:
        screen_x, screen_y = logical_point

    pyautogui.moveTo(screen_x, screen_y, duration=duration)


def pixel(logical_point, window=None, state_name="LE_CHEMINOT"):
    """
    Read the screen-pixel at the logical client-relative point.
    """
    if window is None:
        window = gw.getActiveWindow()

    if window:
        hwnd = window._hWnd
        phys_pt = _scale_for_window(hwnd, logical_point, state_name)
        screen_x, screen_y = _client_to_screen(hwnd, phys_pt)
    else:
        screen_x, screen_y = logical_point

    return pyautogui.pixel(screen_x, screen_y)


def is_pixel_color_match(
    window,
    coords,
    element_name="element",
    expected_colors=None,
    max_attempts=3,
    retry_delay=0.5,
    logger=None,
    tolerance=20,
):
    """
    Universal function to check if a pixel at given coordinates matches any of the expected colors.
    Works for tabs, buttons, status indicators, or any pixel-based detection.
    """
    import time
    from datetime import datetime
    from utils.screenshot import screenshot
    from utils.file_utils import save_file

    # Default to navy blue if no colors provided
    if expected_colors is None:
        expected_colors = [(0, 0, 128)]  # Navy blue RGB

    for attempt in range(1, max_attempts + 1):
        try:
            if window:
                window.activate()
                time.sleep(0.2)

            # Get the color at the specified coordinates
            from utils.coords import pixel  # avoid circular import

            pixel_color = pixel(coords, window=window)

            # Check if the pixel color matches any of the expected colors
            is_match = any(
                abs(pixel_color[0] - color[0]) <= tolerance
                and abs(pixel_color[1] - color[1]) <= tolerance
                and abs(pixel_color[2] - color[2]) <= tolerance
                for color in expected_colors
            )

            if logger:
                logger.debug(
                    f"Pixel at {coords} color: {pixel_color}, Expected one of: {expected_colors}"
                )

            if is_match:
                if logger:
                    logger.debug(
                        f"Pixel color matches one of the expected colors: {pixel_color}"
                    )
                return True
            else:
                if logger:
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts}: Pixel color {pixel_color} doesn't match any expected colors: {expected_colors}"
                    )
                # Take a screenshot for debugging if color doesn't match (only on final attempt)
                if attempt == max_attempts and logger:
                    try:
                        img = screenshot(
                            region=(
                                window.left,
                                window.top,
                                window.width,
                                window.height,
                            )
                        )
                        if img:
                            save_file(
                                img,
                                f"{element_name}_color_mismatch",
                                directory="logs/pixel_screenshots",
                            )
                    except Exception as screenshot_err:
                        logger.error(
                            f"Failed to save debug screenshot: {screenshot_err}"
                        )

                if attempt < max_attempts:
                    time.sleep(retry_delay)
        except Exception as e:
            if logger:
                logger.error(
                    f"Error checking pixel color (attempt {attempt}/{max_attempts}): {e}"
                )
            if attempt < max_attempts:
                time.sleep(retry_delay)
            else:
                return False
    if logger:
        logger.error(
            f"Pixel at {coords} for '{element_name}' did not match expected colors after {max_attempts} attempts."
        )
    return False

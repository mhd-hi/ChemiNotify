import time
import win32gui
import pyautogui
import pygetwindow as gw

from utils.constants.button_coords import REF_WINDOW_SIZES
from utils.logging_config import configure_logging

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
    Click at logical client-relative point inside `window`
    (default state_name="LE_CHEMINOT"). Uses REF_SIZES to scale.
    """
    if window is None:
        window = gw.getActiveWindow()

    if window:
        hwnd = window._hWnd
        phys_pt = _scale_for_window(hwnd, logical_point, state_name)
        screen_x, screen_y = _client_to_screen(hwnd, phys_pt)
    else:
        screen_x, screen_y = logical_point

    _nudge_from_corners()
    moveTo(
        logical_point=logical_point,
        window=window,
        duration=0.10,
        state_name=state_name,
    )
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

    _nudge_from_corners()
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
):
    """
    Universal function to check if a pixel at given coordinates exactly matches any of the expected colors.
    Works for tabs, buttons, status indicators, or any pixel-based detection.
    """
    import time
    from datetime import datetime
    from commands.screenshot import screenshot
    from utils.file_utils import save_file

    if expected_colors is None or len(expected_colors) == 0:
        logger.error(
            f"No expected colors provided for '{element_name}'. Cannot perform color matching."
        )
        return False

    for attempt in range(1, max_attempts + 1):
        try:
            if window:
                window.activate()
                time.sleep(0.2)

            from commands.coords import pixel

            pixel_color = pixel(coords, window=window)

            is_match = pixel_color in expected_colors

            logger.debug(
                f"Pixel at {coords} color: {pixel_color}, Expected one of: {expected_colors}"
            )

            if is_match:
                logger.debug(
                    f"Pixel color exactly matches one of the expected colors: {pixel_color}"
                )
                return True
            else:
                logger.warning(
                    f"Attempt {attempt}/{max_attempts}: Pixel color {pixel_color} doesn't match any expected colors: {expected_colors}"
                )

                # Screenshot for debugging if the pixel color does not match
                if attempt == max_attempts:
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
                                directory="logs/screenshots",
                            )
                    except Exception as screenshot_err:
                        logger.error(
                            f"Failed to save debug screenshot: {screenshot_err}"
                        )

                if attempt < max_attempts:
                    time.sleep(retry_delay)
        except Exception as e:
            logger.error(
                f"Error checking pixel color (attempt {attempt}/{max_attempts}): {e}"
            )
            if attempt < max_attempts:
                time.sleep(retry_delay)
            else:
                return False

    logger.error(
        f"Pixel at {coords} for '{element_name}' did not match expected colors after {max_attempts} attempts."
    )
    return False


def _nudge_from_corners():
    """
    Moves the mouse cursor away from screen corners to avoid pyautogui failsafe exceptions.
    """
    try:
        w, h = pyautogui.size()
        x, y = pyautogui.position()
        if x <= 1 or y <= 1 or x >= w - 2 or y >= h - 2:
            # move to center to clear fail-safe zone
            pyautogui.moveTo(w // 2, h // 2, duration=0.12)
            time.sleep(0.05)
    except Exception:
        pass

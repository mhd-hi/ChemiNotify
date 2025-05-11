
import ctypes, win32gui, pyautogui, pygetwindow as gw

from utils.constants.button_coords import REF_WINDOW_SIZES

def _client_to_screen(hwnd, point):
    """Win32 ClientToScreen in physical px; returns (x,y) in physical px."""
    ox, oy = win32gui.ClientToScreen(hwnd, (0, 0))
    return ox + point[0], oy + point[1]

def _scale_for_window(hwnd, logical_point, state_name):
    """Turn a logical_point in your design coords into a physical client px tuple."""
    ref_w, ref_h = REF_WINDOW_SIZES.get(state_name)
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

def moveTo(logical_point, window=None, duration=0, state_name="LE_CHEMINOT"):
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
    Read the screen‐pixel at the logical client-relative point.
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
import time
import pygetwindow as gw
from typing import Set, Optional

def list_window_titles() -> Set[str]:
    """Return the set of all non-empty window titles right now."""
    return {w.title for w in gw.getAllWindows() if w.title.strip()}

def wait_for_new_window(
    before: Set[str],
    timeout: float = 2.0,
    poll: float = 0.1,
    ignore: Optional[Set[str]] = None
) -> Optional[str]:
    """
    Poll for up to `timeout` seconds for a window title to appear
    that wasn't in `before`.  Returns the new title, or None if none arrive.
    """
    ignore = ignore or set()
    deadline = time.time() + timeout

    while time.time() < deadline:
        now = list_window_titles()
        diff = now - before - ignore
        if diff:
            # return the first new title we see
            return diff.pop()
        time.sleep(poll)

    return None

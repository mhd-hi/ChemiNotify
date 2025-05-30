import ctypes

from utils.file_utils import cleanup_old_screenshots

DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(
        DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
    )
except (AttributeError, OSError):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDpiAware()

import os
import sys
import time
import dotenv
import pytesseract

dotenv.load_dotenv()

from states.manager import StateManager
from states.initial_state import InitialState
from states.login_state import LoginState
from states.consultation_state import ConsultationState
from states.inscription_state import InscriptionState
from states.selection_cours_state import SelectionCoursState
from states.horaire_state import HoraireState
from states.exit_state import ExitState
from states.state_types import StateType
from utils.logging_config import configure_logging

required_files = {
    "JNLP file": os.getenv("CHEMINOT_FILE_PATH"),
    "Tesseract executable": os.getenv(
        "TESSERACT_CMD", "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    ),
}
missing = [
    name
    for name, path in required_files.items()
    if not path or not os.path.isfile(path)
]

pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD")


def main():
    logger = configure_logging("Main")
    logger.info("=== Starting ChemiNotify ===")

    if missing:
        logger.error(f"Missing files: {', '.join(missing)}")
        sys.exit(1)

    try:
        cleanup_old_screenshots(days=7)

        SESSION_DURATION_MINUTES = int(os.getenv("SESSION_DURATION_MINUTES", 32))

        while True:
            # Fresh state instances each session
            states = {
                StateType.INITIAL: InitialState(),
                StateType.LOGIN: LoginState(),
                StateType.CONSULTATION: ConsultationState(),
                StateType.INSCRIPTION: InscriptionState(),
                StateType.SELECTION_COURS: SelectionCoursState(),
                StateType.HORAIRE: HoraireState(),
                StateType.EXIT: ExitState(),
            }

            manager = StateManager(
                states=states,
                initial_state=StateType.INITIAL,
                session_timeout=SESSION_DURATION_MINUTES * 60,
            )

            logger.info(
                f"-> Starting new session of up to {SESSION_DURATION_MINUTES} minutes"
            )
            manager.run()

            logger.info("Session ended (timeout or terminal). Restarting in 5 seconds…")
            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down.")
    finally:
        logger.info("=== ChemiNotify Finished ===")


if __name__ == "__main__":
    main()

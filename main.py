import ctypes

DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = -4
try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2)
except (AttributeError, OSError):
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDpiAware()

import logging
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
from utils.logging_config import configure_logging

required_files = {
    'JNLP file': os.getenv('JNLP_PATH'),
    'Tesseract executable': os.getenv('TESSERACT_CMD'),
}
missing = [name for name, path in required_files.items() if not path or not os.path.isfile(path)]

pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_CMD')

def main():
    logger = configure_logging("Main")
    logger.info("=== Starting ChemiNotify ===")

    if missing:
        logging.error(f"Missing files: {', '.join(missing)}")
        sys.exit(1)
    
    try:
        SESSION_DURATION_MINUTES = int(os.getenv('SESSION_DURATION_MINUTES'))
    
        # Loop forever: each pass is one session-duration
        while True:
            # Fresh state instances each session
            states = {
                "INITIAL":        InitialState(),
                "LOGIN":          LoginState(),
                "CONSULTATION":   ConsultationState(),
                "INSCRIPTION":    InscriptionState(),
                "SELECTION_COURS":SelectionCoursState(),
                "HORAIRE":        HoraireState(),
                "EXIT":           ExitState(),
            }

            manager = StateManager(
                states,
                initial_state="INITIAL",
                session_timeout=SESSION_DURATION_MINUTES * 60
            )

            logger.info(f"-> Starting new session of up to {SESSION_DURATION_MINUTES} minutes")
            manager.run()

            logger.info("Session ended (timeout or terminal). Restarting in 5 seconds…")
            time.sleep(5)

    except KeyboardInterrupt:
        logger.info("Interrupted by user, shutting down.")
    finally:
        logger.info("=== ChemiNotify Finished ===")

if __name__ == "__main__":
    main()

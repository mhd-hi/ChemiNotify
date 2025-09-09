import os
import logging


def configure_logging(name="Logger"):
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    os.makedirs("logs", exist_ok=True)
    os.makedirs("logs/screenshots", exist_ok=True)
    os.makedirs("logs/ocr_screenshots", exist_ok=True)

    handlers = [
        logging.StreamHandler(),
        logging.FileHandler("logs/cheminotify.log", mode="a"),
        logging.FileHandler("logs/error.log", mode="a"),
    ]

    # Set error.log to only log ERROR and above
    error_handler = handlers[2]
    error_handler.setLevel(logging.ERROR)

    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,
    )

    return logging.getLogger(name)

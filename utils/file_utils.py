import os
import time
import glob
import datetime
from typing import Optional, List
from utils.logging_config import configure_logging

logger = configure_logging(__name__)


def save_file(
    file_data,
    base_name: str,
    directory: str = "logs/screenshots",
    extension: str = "png",
    timestamp: bool = True,
    suffix: Optional[str] = None,
) -> Optional[str]:
    """
    Generic utility to save a file to disk with standardized naming and error handling.

    Args:
        file_data: The data to save (e.g., PIL Image)
        base_name: Base name for the file
        directory: Directory to save the file
        extension: File extension (without dot)
        timestamp: Whether to add timestamp to filename
        suffix: Optional suffix to add to filename

    Returns:
        Path to the saved file or None if there was an error
    """
    filepath = None
    try:
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)

        # Build filename
        name_parts = [base_name]
        if suffix:
            name_parts.append(suffix)

        # Add timestamp if requested
        if timestamp:
            timestamp_str = time.strftime("%Y%m%d-%H%M%S")
            filename = f"{timestamp_str}_{'_'.join(name_parts)}.{extension}"
        else:
            filename = f"{'_'.join(name_parts)}.{extension}"

        filepath = os.path.join(directory, filename)

        if hasattr(file_data, "save"):  # For PIL Image objects
            file_data.save(filepath)
        elif isinstance(file_data, bytes):
            with open(filepath, "wb") as f:
                f.write(file_data)
        elif isinstance(file_data, str):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(file_data)
        else:
            logger.error(f"Unsupported file data type: {type(file_data)}")
            return None

        logger.debug(f"File saved: {filepath}")
        return filepath
    except Exception as e:
        logger.error(f"Error saving file: {str(e)}")
        if filepath:
            logger.error(f"Error occurred while saving to: {filepath}")
        return None


def cleanup_old_screenshots(
    days: int = 7, directories: Optional[List[str]] = None
) -> int:
    """
    Delete screenshot files older than the specified number of days.

    Args:
        days: Number of days to keep files (older files will be deleted)
        directories: List of directories to clean (defaults to all screenshot directories)

    Returns:
        Number of files deleted
    """
    if directories is None:
        directories = [
            "logs/screenshots",
            "logs/ocr_screenshots",
            "logs/pixel_screenshots",
        ]

    current_time = time.time()
    max_age = days * 24 * 60 * 60  # Convert days to seconds
    deleted_count = 0

    logger.info(f"Cleaning up screenshots older than {days} days...")

    for directory in directories:
        if not os.path.exists(directory):
            logger.debug(f"Directory doesn't exist, skipping: {directory}")
            continue

        # Get all PNG files in the directory
        pattern = os.path.join(directory, "*.png")
        files = glob.glob(pattern)

        for file_path in files:
            file_age = current_time - os.path.getmtime(file_path)
            if file_age > max_age:
                try:
                    os.remove(file_path)
                    deleted_count += 1
                    logger.debug(f"Deleted old screenshot: {file_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete {file_path}: {str(e)}")

    logger.info(f"Cleanup completed: {deleted_count} files deleted")
    return deleted_count

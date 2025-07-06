# Code Structure

The ChemiNotify codebase is organized following best practices for separation of concerns between commands and utilities.

## Directory Organization

### `commands/`
Contains specific actions and entry-point modules that perform concrete operations:

- **`coords.py`** - Click operations and coordinate manipulation commands
  - Functions: `click()`, `moveTo()`, `is_pixel_color_match()`, `pixel()`
  - Handles window scaling and coordinate transformations
  - Manages mouse interactions with the application

- **`screenshot.py`** - Screenshot capture and processing commands  
  - Functions: `screenshot()`, `take_debug_screenshot()`
  - Captures screen regions and full screenshots
  - Handles window-specific screenshot cropping

- **`popup_detector.py`** - Popup detection and handling commands
  - Class: `PopupDetector`
  - Detects and handles various popup windows
  - Manages popup interactions and responses

### `utils/`
Contains reusable helper code that supports the commands:

- **`file_utils.py`** - Generic file operations and utilities
  - Functions: `save_file()`, `cleanup_old_screenshots()`
  - Handles file I/O operations with standardized naming
  - Manages log file cleanup

- **`logging_config.py`** - Logging configuration setup
  - Function: `configure_logging()`
  - Sets up structured logging for the application
  - Configures log levels and output destinations

- **`window_helpers.py`** - Window management utilities
  - Functions: `list_window_titles()`, `wait_for_new_window()`
  - Provides window detection and management utilities
  - Handles window polling and discovery

- **`constants/`** - Configuration constants and coordinate data
  - `button_coords.py` - UI element coordinates and reference sizes
  - `texts.py` - Text patterns for popup detection

## Design Principles

### Commands vs Utils
- **Commands** perform specific actions (clicking, taking screenshots, detecting popups)
- **Utils** provide reusable helper functionality (file operations, logging, window management)

### Import Structure
- State files import from `commands.` for actions they need to perform
- All modules import from `utils.` for supporting functionality
- Commands may import from other commands when needed
- Utils should not import from commands (to avoid circular dependencies)

### Benefits
1. **Clear separation of concerns** - Easy to understand what each module does
2. **Better maintainability** - Commands and utilities are organized logically
3. **Improved testability** - Commands can be tested independently
4. **Scalability** - Easy to add new commands or utilities in the right place

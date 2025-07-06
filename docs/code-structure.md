# Code Structure

This document provides a comprehensive overview of the ChemiNotify codebase architecture and organization.

## Project Overview

ChemiNotify is a Python-based automation tool that monitors course availability in the Cheminot system using image recognition and UI automation techniques.

## Architecture

The application follows a **state machine pattern** with supporting command and utility modules:

```
ChemiNotify/
├── main.py                 # Application entry point
├── states/                 # State machine implementation
├── commands/               # Action-oriented modules
├── utils/                  # Reusable helper utilities
├── notifications/          # Notification system
├── docs/                   # Documentation
└── logs/                   # Runtime logs and screenshots
```

## Core Components

### 1. Main Application (`main.py`)
- **Purpose**: Application entry point and session management
- **Key Features**:
  - DPI awareness configuration for Windows
  - Session loop with timeout handling
  - State machine initialization
  - Error handling and logging

### 2. State Machine (`states/`)
The application's core logic is organized as a finite state machine:

- **`manager.py`** - State machine coordinator
  - Manages state transitions and session timeout
  - Handles global error recovery
  - Provides state debugging capabilities

- **`base.py`** - Abstract base class for all states
  - Defines common state interface
  - Provides logging and screenshot utilities
  - Implements state transition validation

- **State Implementations**:
  - `initial_state.py` - Application startup and window detection
  - `login_state.py` - User authentication handling
  - `consultation_state.py` - Course consultation interface
  - `inscription_state.py` - Course enrollment process
  - `selection_cours_state.py` - Course selection interface
  - `horaire_state.py` - Schedule management
  - `exit_state.py` - Application shutdown

- **`state_types.py`** - State enumeration and type definitions

### 3. Commands (`commands/`)
Action-oriented modules that perform specific operations:

- **`coords.py`** - Mouse and coordinate operations
  - Window scaling and coordinate transformation
  - Click operations with window awareness
  - Pixel color detection and matching
  - Client-to-screen coordinate conversion

- **`screenshot.py`** - Screen capture operations
  - Full screen and region-based screenshots
  - Window-specific screenshot cropping
  - Debug screenshot functionality with conditional logging

- **`popup_detector.py`** - Popup window management
  - Automated popup detection and classification
  - Window title and content matching
  - Popup handling strategies (close, interact, ignore)
  - OCR-based text recognition for popup content

### 4. Utilities (`utils/`)
Reusable helper modules that support the commands:

- **`file_utils.py`** - File system operations
  - Generic file saving with timestamp and naming conventions
  - Log file cleanup and maintenance
  - Screenshot file management

- **`logging_config.py`** - Logging infrastructure
  - Centralized logging configuration
  - Log level management from environment variables
  - Multi-destination logging (console + file)

- **`window_helpers.py`** - Window management utilities
  - Window enumeration and filtering
  - Window state monitoring
  - New window detection with polling

- **`constants/`** - Configuration and constants
  - `button_coords.py` - UI element coordinates and reference window sizes
  - `texts.py` - Text patterns for popup detection and window identification

### 5. Notifications (`notifications/`)
Multi-channel notification system:

- **`base.py`** - Abstract notification interface
- **`discord.py`** - Discord webhook notifications
- **`email.py`** - Email notification support
- **`facade.py`** - Notification manager and dispatcher

## Data Flow

1. **Initialization**: Main application starts, configures logging and DPI awareness
2. **State Machine**: StateManager initializes with all state instances
3. **State Execution**: Each state performs its specific operations using commands
4. **Commands**: Execute UI automation tasks (clicking, screenshots, popup handling)
5. **Utilities**: Provide supporting functionality (file operations, logging, window management)
6. **Notifications**: Send alerts when courses become available
7. **Session Management**: Handle timeouts and restart cycles

## Key Design Patterns

### State Machine Pattern
- **Purpose**: Manages complex application flow with clear state transitions
- **Benefits**: Predictable behavior, easy debugging, clear separation of concerns

### Command Pattern
- **Purpose**: Encapsulates UI automation operations as discrete commands
- **Benefits**: Reusable operations, easier testing, clear action semantics

### Facade Pattern
- **Purpose**: Simplifies notification system interactions
- **Benefits**: Clean interface, multiple notification channels, easy extension

## Configuration Management

- **Environment Variables**: `.env` file for sensitive configuration
- **Constants**: Hardcoded coordinates and text patterns in `utils/constants/`
- **Runtime Configuration**: Log levels, timeouts, and paths

## Error Handling Strategy

- **Graceful Degradation**: Application continues running despite individual operation failures
- **Comprehensive Logging**: All operations logged with appropriate levels
- **Screenshot Evidence**: Debug screenshots captured for troubleshooting
- **Session Recovery**: Automatic restart on critical failures

## Testing and Debugging

- **Debug Screenshots**: Conditional screenshot capture based on log level
- **Comprehensive Logging**: Detailed operation logging for troubleshooting
- **State Validation**: State transition validation and error reporting
- **Window Detection**: Robust window finding and interaction verification

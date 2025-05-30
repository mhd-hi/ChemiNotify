import time
import traceback
import os
from typing import Dict, Optional, Union
from utils.logging_config import configure_logging
from .base import AppState
from .state_types import StateType


class StateManager:
    """Manages application states, transitions, and enforces a session timeout."""

    def __init__(
        self,
        states: Dict[StateType, AppState],
        initial_state: StateType = StateType.INITIAL,
        session_timeout: Optional[int] = None,  # in seconds
    ):
        self.states = states
        self.current_state_name = initial_state
        self.session_timeout = session_timeout
        self.session_start_time = None
        self.logger = configure_logging(self.__class__.__name__)

    def take_error_screenshot(self, error_name: str = "state_manager_error"):
        """Takes a screenshot when an error occurs (only in DEBUG mode)"""
        if os.getenv("LOG_LEVEL", "").upper() != "DEBUG":
            return None

        try:
            from utils.screenshot import take_debug_screenshot

            return take_debug_screenshot(error_name)
        except Exception as e:
            self.logger.error(f"Failed to take error screenshot: {str(e)}")
            return None

    def run(self):
        """Main state machine loop"""
        self.session_start_time = time.time()

        while True:
            # Check if we need to exit based on the current state
            if self.current_state_name == StateType.EXIT:
                self.logger.info("Exiting state machine")
                break

            # Check session timeout if enabled
            if (
                self.session_timeout
                and time.time() - self.session_start_time > self.session_timeout
            ):
                self.logger.info(
                    f"Session timeout reached ({self.session_timeout / 60:.1f} minutes)"
                )
                if StateType.EXIT in self.states:
                    self.current_state_name = StateType.EXIT
                    continue
                else:
                    break

            try:
                current_state = self.states.get(self.current_state_name)
                if not current_state:
                    self.logger.error(
                        f"No handler for state: {self.current_state_name}"
                    )
                    break

                # Process the current state and get the next state
                next_state = current_state.handle()
                self.logger.info(
                    f"State transition: {self.current_state_name} -> {next_state}"
                )
                self.current_state_name = next_state

            except Exception as e:
                self.logger.error(f"Error in state {self.current_state_name}: {e}")
                self.logger.error(traceback.format_exc())
                if StateType.EXIT in self.states:
                    self.current_state_name = StateType.EXIT
                else:
                    break

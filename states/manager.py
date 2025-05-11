import time
import logging
from typing import Dict
import traceback
import os
from .base import AppState

class StateManager:
    """Manages application states, transitions, and enforces a session timeout."""

    def __init__(
        self,
        states: Dict[str, AppState],
        initial_state: str = "INITIAL",
        session_timeout: int = None, # in seconds
    ):
        self.states = states
        self.current_state_name = initial_state
        self.session_timeout = session_timeout
        self.session_start_time = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def take_error_screenshot(self, error_name: str = "state_manager_error"):
        """Takes a screenshot when an error occurs (only in DEBUG mode)"""
        if os.getenv('LOG_LEVEL', '').upper() != 'DEBUG':
            return None

        try:
            from utils.screenshot import take_debug_screenshot
            return take_debug_screenshot(error_name)
        except Exception as e:
            self.logger.error(f"Failed to take error screenshot: {str(e)}")
            return None

    def run(self) -> None:
        """Run the state machine until a terminal state or session timeout."""
        self.session_start_time = time.time()
        self.logger.info("=== Starting State Machine ===")

        while True:
            self.logger.info(f"CURRENT STATE: {self.current_state_name}")

            # --- SESSION TIMEOUT CHECK ---
            if self.session_timeout is not None:
                elapsed = time.time() - self.session_start_time
                if elapsed >= self.session_timeout:
                    self.logger.info(
                        f"Session timeout reached ({elapsed:.0f}s >= {self.session_timeout}s), initiating EXIT state"
                    )
                    exit_state = self.states.get("EXIT")
                    if exit_state:
                        try:
                            exit_state.handle()
                        except Exception as e:
                            self.logger.error(f"Error in EXIT state during timeout: {e}")
                    else:
                        self.logger.warning("No EXIT state defined in StateManager")
                    break

            # --- STATE HANDLING ---
            if self.current_state_name not in self.states:
                error_msg = f"No handler for state '{self.current_state_name}'"
                self.logger.error(error_msg)
                self.take_error_screenshot(f"invalid_state_{self.current_state_name}")
                break

            current_state = self.states[self.current_state_name]

            try:
                self.logger.info(f"Executing {self.current_state_name} handler...")
                next_state = current_state.handle()
                self.logger.info(f"State transition: {self.current_state_name} -> {next_state}")
            except Exception as e:
                self.logger.error(f"Error in state {self.current_state_name}: {e}")
                self.take_error_screenshot(f"exception_{self.current_state_name}")
                traceback.print_exc()
                break

            # Terminal state: Stop looping.
            if next_state is None:
                self.logger.info("Reached terminal state, exiting state machine")
                break

            self.logger.info(f"{'='*4}\nTransitioning to new state: {next_state}\n{'='*4}")
            self.current_state_name = next_state

            # Small delay between states
            time.sleep(1)

        self.logger.info("=== State machine execution complete ===")

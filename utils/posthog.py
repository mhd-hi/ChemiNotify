import os
import uuid
import socket
import json
import logging
from pathlib import Path
from urllib.parse import urlparse

from posthog import Posthog

logger = logging.getLogger(__name__)

# Configuration

# PostHog API key intended to be visible, since it's only used for sending events
POSTHOG_API_KEY = "phc_1RDgY4dpBlUNYRdZKH2WlOAFydNZcrXfMFkIpKSONfU"
POSTHOG_HOST = "https://us.i.posthog.com"
USER_DATA_FILE = Path("user_data.json")


def initialize_posthog():
    """
    Initialize PostHog telemetry with user consent handling.
    Returns (PostHog client, user_id) if telemetry is enabled and reachable,
    otherwise (None, user_id).
    """
    # Retrieve or create user ID and existing consent flag
    user_id, telemetry_enabled = get_or_create_user_data()

    # If it's the first run, ask for consent and save it
    if telemetry_enabled is None:
        telemetry_enabled = ask_for_consent()
        save_user_data(user_id, telemetry_enabled)

    # If telemetry is enabled, do a DNS preflight on the host
    if telemetry_enabled:
        host = urlparse(POSTHOG_HOST).hostname
        try:
            socket.getaddrinfo(host, 443)
        except socket.gaierror as e:
            logger.warning(
                f"Could not resolve PostHog host '{host}'—disabling telemetry."
            )
            logger.debug(f"DNS resolution failed for '{host}': {str(e)}")
            return None, user_id

        logger.info("Telemetry enabled with anonymous ID")
        posthog_client = Posthog(
            project_api_key=POSTHOG_API_KEY,
            host=POSTHOG_HOST,
            sync_mode=True,
        )

        # Send a single 'app_started' event with the user ID (uuid)
        try:
            posthog_client.capture(distinct_id=user_id, event="app_started")
            logger.debug("Successfully sent initial telemetry event")
        except Exception as e:
            logger.error(f"Failed to send telemetry: {e}")
            return None, user_id

        return posthog_client, user_id

    logger.info("Telemetry disabled by user preference")
    return None, user_id


def get_or_create_user_data():
    """
    Retrieve or create user ID and telemetry preference.
    Returns (user_id, telemetry_enabled) where telemetry_enabled is:
      - True/False from saved preference
      - None if no preference saved yet
    """
    try:
        if USER_DATA_FILE.exists():
            with open(USER_DATA_FILE, "r") as f:
                data = json.load(f)
                return data.get("user_id"), data.get("telemetry_enabled")
        else:
            # Generate a fresh UUID for this user
            user_id = str(uuid.uuid4())
            return user_id, None
    except Exception as e:
        logger.error(f"Error accessing user data file: {e}")
        return str(uuid.uuid4()), None


def save_user_data(user_id, telemetry_enabled):
    """Save user ID and telemetry preference to file"""
    try:
        with open(USER_DATA_FILE, "w") as f:
            json.dump({"user_id": user_id, "telemetry_enabled": telemetry_enabled}, f)
        return True
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
        return False


def ask_for_consent():
    """Ask the user for telemetry consent via terminal prompt"""
    print("Would you allow the app to send anonymous usage statistics?")
    print(
        "This only sends a random ID when the app starts to help me analyze how many people are using ChemiNotify (purely for stats purposes)."
    )

    while True:
        response = input("Enable anonymous usage analytics? (y/n): ").strip().lower()
        if response in ("y", "yes"):
            print("Anonymous telemetry enabled.")
            return True
        elif response in ("n", "no"):
            print("Telemetry disabled.")
            return False
        else:
            print("Please enter 'y' or 'n'.")

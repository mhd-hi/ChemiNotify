import uuid
import socket
import json
import logging
from pathlib import Path
from urllib.parse import urlparse

from posthog import Posthog

logger = logging.getLogger(__name__)

# PostHog API key intended to be visible, since it's only used for sending events
POSTHOG_API_KEY = "phc_1RDgY4dpBlUNYRdZKH2WlOAFydNZcrXfMFkIpKSONfU"
POSTHOG_HOST = "https://us.i.posthog.com"
USER_DATA_FILE = Path("user_data.json")


def initialize_posthog():
    user_id, telemetry_enabled = get_or_create_user_data()

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
    try:
        if USER_DATA_FILE.exists():
            with open(USER_DATA_FILE, "r") as f:
                data = json.load(f)
                return data.get("user_id"), data.get("telemetry_enabled")
        else:
            user_id = str(uuid.uuid4())
            return user_id, None
    except Exception as e:
        logger.error(f"Error accessing user data file: {e}")
        return str(uuid.uuid4()), None


def save_user_data(user_id, telemetry_enabled):
    try:
        with open(USER_DATA_FILE, "w") as f:
            json.dump({"user_id": user_id, "telemetry_enabled": telemetry_enabled}, f)
        return True
    except Exception as e:
        logger.error(f"Error saving user data: {e}")
        return False


def ask_for_consent():
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

import os

from .base import NotificationChannel
from .discord import DiscordNotification

class NotificationFacade:
    """
    Facade to send notifications via multiple channels.
    """
    def __init__(self, channels: list[NotificationChannel] = None):
        if channels:
            self._channels = channels
        else:
            self._channels = []
            # Auto-register channels if ENV vars present
            if os.getenv('DISCORD_WEBHOOK_URL'):
                self._channels.append(DiscordNotification())

    def register(self, channel: NotificationChannel) -> None:
        """Register a new notification channel at runtime."""
        self._channels.append(channel)

    def send(self, subject: str, body: str) -> dict[str,bool]:
        """
        Send the given subject and body to all registered channels.
        Returns a dict mapping channel class names to send status.
        """
        results = {}
        for channel in self._channels:
            name = channel.__class__.__name__
            results[name] = channel.send(subject, body)
        return results
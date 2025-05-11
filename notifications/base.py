from abc import ABC, abstractmethod

class NotificationChannel(ABC):
    """
    Base interface for notification channels.
    """

    @abstractmethod
    def send(self, subject: str, body: str) -> bool:
        """
        Send a notification with the given subject and body.

        Returns True on success, False otherwise.
        """
        pass
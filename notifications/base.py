from abc import ABC, abstractmethod
import logging


class NotificationChannel(ABC):
    """
    Base interface for notification channels.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def send(self, subject: str, body: str) -> bool:
        """
        Send a notification with the given subject and body.

        Returns True on success, False otherwise.
        """
        self.logger.warning(
            "This is an abstract method and should be implemented by subclasses"
        )
        return False

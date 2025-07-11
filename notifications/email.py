from dotenv import load_dotenv

from .base import NotificationChannel

load_dotenv()


class EmailNotification(NotificationChannel):
    """
    Notification channel to send emails.
    """

    def __init__(self):
        super().__init__()

    def send(self, subject: str, body: str) -> bool:
        # implement email logic
        return True

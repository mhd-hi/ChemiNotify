import os
import requests
from typing import Optional
from utils.logging_config import configure_logging

from .base import NotificationChannel

class DiscordNotification(NotificationChannel):
    """
    Notification channel to send messages to Discord via webhook.
    """
    def __init__(self, webhook_url: Optional[str] = os.getenv('DISCORD_WEBHOOK_URL')):
        self.webhook_url = webhook_url
        self.logger = configure_logging(self.__class__.__name__)
        self.include_screenshots = os.getenv('NOTIFICATION_INCLUDE_SCREENSHOTS', '1') != '0'

    def send(self, subject: str, body: str, image_path: Optional[str] = None) -> bool:
        """
        Send a Discord notification, optionally with an image attachment.
        
        Args:
            subject: The notification subject
            body: The notification message body
            image_path: Optional path to an image file to include
            
        Returns:
            True if successful, False otherwise
        """
        if not self.webhook_url:
            self.logger.warning("No webhook URL configured.")
            return False

        if not self.include_screenshots or not image_path:
            return self._send_text_message(subject, body)

        if not os.path.exists(image_path):
            self.logger.warning(f"Image file not found: {image_path}")
            return self._send_text_message(subject, body)
        
        # Sending with image
        try:
            message_content = f"**{subject}**\n{body}"
            
            with open(image_path, 'rb') as img:
                files = {
                    'file': (os.path.basename(image_path), img, 'image/png')
                }
                payload = {'content': message_content}
                
                resp = requests.post(
                    self.webhook_url, 
                    data=payload,
                    files=files
                )
                
            if resp.status_code in (200, 204):
                self.logger.info(f"Sent with image: {subject}")
                return True
            else:
                self.logger.error(f"Failed to send with image ({resp.status_code}): {resp.text}")
                return self._send_text_message(subject, body)
        except Exception as e:
            self.logger.exception(f"Exception when sending Discord notification with image: {e}")
            return self._send_text_message(subject, body)

    def _send_text_message(self, subject: str, body: str) -> bool:
        if not self.webhook_url:
            self.logger.error("No webhook URL configured for text message.")
            return False
            
        payload = {
            'content': f"**{subject}**\n{body}"
        }
        try:
            resp = requests.post(self.webhook_url, json=payload)
            if resp.status_code in (200, 204):
                self.logger.info(f"Sent with text message only: {subject}")
                return True
            else:
                self.logger.error(f"Failed ({resp.status_code}): {resp.text}")
                return False
        except Exception as e:
            self.logger.exception(f"Exception when sending Discord notification: {e}")
            return False
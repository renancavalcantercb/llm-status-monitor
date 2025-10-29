"""
Notification handlers for Discord and Slack
"""

import logging
import requests
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class NotificationError(Exception):
    """Base exception for notification errors"""
    pass


class Notifier(ABC):
    """Abstract base class for notification services"""

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    @abstractmethod
    def send(
        self,
        service_name: str,
        title: str,
        description: str,
        link: str,
        color: int
    ) -> bool:
        """Send a notification. Returns True on success, False on failure."""
        pass


class DiscordNotifier(Notifier):
    """Discord webhook notifier"""

    def send(
        self,
        service_name: str,
        title: str,
        description: str,
        link: str,
        color: int
    ) -> bool:
        """Send notification to Discord webhook"""
        embed = {
            "title": f"🚨 {service_name} Status Update",
            "description": title,
            "url": link,
            "color": color,
            "fields": [
                {
                    "name": "Details",
                    "value": description[:1024] if description else "No additional details",
                    "inline": False
                }
            ],
            "footer": {
                "text": f"LLM Status Monitor • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
        }

        payload = {"embeds": [embed]}

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Discord notification sent for {service_name}")
            return True
        except requests.exceptions.Timeout:
            logger.error(f"Discord notification timeout for {service_name}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Discord notification failed for {service_name}: {e}")
            return False


class SlackNotifier(Notifier):
    """Slack webhook notifier"""

    # Color mapping for Slack
    COLOR_MAP = {
        0xD97757: '#D97757',  # Claude orange/brown
        0x10A37F: '#10A37F',  # OpenAI green
    }

    def send(
        self,
        service_name: str,
        title: str,
        description: str,
        link: str,
        color: int
    ) -> bool:
        """Send notification to Slack webhook"""
        slack_color = self.COLOR_MAP.get(color, '#FF0000')  # Default to red

        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"🚨 {service_name} Status Update",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{title}*\n\n{description[:2000] if description else 'No additional details'}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<{link}|View full details on status page>"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"LLM Status Monitor • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]

        payload = {
            "blocks": blocks,
            "attachments": [
                {
                    "color": slack_color,
                    "fallback": f"{service_name}: {title}"
                }
            ]
        }

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Slack notification sent for {service_name}")
            return True
        except requests.exceptions.Timeout:
            logger.error(f"Slack notification timeout for {service_name}")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Slack notification failed for {service_name}: {e}")
            return False


def create_notifier(notification_type: str, webhook_url: str) -> Optional[Notifier]:
    """
    Factory function to create the appropriate notifier.

    Args:
        notification_type: Either 'discord' or 'slack'
        webhook_url: The webhook URL to send notifications to

    Returns:
        A Notifier instance, or None if type is unknown
    """
    if notification_type == 'discord':
        return DiscordNotifier(webhook_url)
    elif notification_type == 'slack':
        return SlackNotifier(webhook_url)
    else:
        logger.error(f"Unknown notification type: {notification_type}")
        return None

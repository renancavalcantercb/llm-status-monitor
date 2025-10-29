"""
Configuration management for LLM Status Monitor
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional, Literal
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

NotificationType = Literal["discord", "slack"]


@dataclass
class FeedConfig:
    """Configuration for an RSS feed"""
    name: str
    url: str
    color: int


@dataclass
class Config:
    """Main configuration class"""
    notification_type: NotificationType
    discord_webhook: Optional[str]
    slack_webhook: Optional[str]
    check_interval: int
    state_file: Path

    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables"""
        load_dotenv()

        notification_type = os.getenv('NOTIFICATION_TYPE', 'discord').lower()

        # Validate notification type
        if notification_type not in ('discord', 'slack'):
            raise ValueError(
                f"Invalid NOTIFICATION_TYPE: {notification_type}. "
                f"Must be 'discord' or 'slack'"
            )

        discord_webhook = os.getenv('DISCORD_WEBHOOK_URL')
        slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        check_interval = int(os.getenv('CHECK_INTERVAL', '300'))
        state_file = Path(os.getenv('STATE_FILE', 'data/state.json'))

        # Validate webhook configuration
        if notification_type == 'discord' and not discord_webhook:
            logger.warning(
                "NOTIFICATION_TYPE is 'discord' but DISCORD_WEBHOOK_URL is not set"
            )
        elif notification_type == 'slack' and not slack_webhook:
            logger.warning(
                "NOTIFICATION_TYPE is 'slack' but SLACK_WEBHOOK_URL is not set"
            )

        # Validate check interval
        if check_interval < 10:
            logger.warning(
                f"CHECK_INTERVAL ({check_interval}s) is very low. "
                f"Consider using at least 60 seconds."
            )

        return cls(
            notification_type=notification_type,
            discord_webhook=discord_webhook,
            slack_webhook=slack_webhook,
            check_interval=check_interval,
            state_file=state_file
        )

    def is_configured(self) -> bool:
        """Check if notifications are properly configured"""
        if self.notification_type == 'discord':
            return bool(self.discord_webhook)
        elif self.notification_type == 'slack':
            return bool(self.slack_webhook)
        return False

    def get_webhook_url(self) -> Optional[str]:
        """Get the appropriate webhook URL based on notification type"""
        if self.notification_type == 'discord':
            return self.discord_webhook
        elif self.notification_type == 'slack':
            return self.slack_webhook
        return None


# RSS Feed configurations
FEEDS: dict[str, FeedConfig] = {
    'claude': FeedConfig(
        name='Anthropic (Claude)',
        url='https://status.claude.com/history.rss',
        color=0xD97757  # Orange/brown
    ),
    'chatgpt': FeedConfig(
        name='OpenAI (ChatGPT)',
        url='https://status.openai.com/history.rss',
        color=0x10A37F  # Green
    )
}

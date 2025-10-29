"""
Main monitoring logic for LLM Status Monitor
"""

import time
import logging
from datetime import datetime
from typing import Optional

from .config import Config, FEEDS, FeedConfig
from .notifiers import create_notifier, Notifier
from .filters import IncidentFilter
from .feed_parser import FeedParser
from .state import StateManager

logger = logging.getLogger(__name__)


class StatusMonitor:
    """Main status monitoring orchestrator"""

    def __init__(self, config: Config):
        self.config = config
        self.state_manager = StateManager(config.state_file)
        self.notifier: Optional[Notifier] = None
        self.filter = IncidentFilter()
        self.parser = FeedParser()

        # Initialize notifier if configured
        webhook_url = config.get_webhook_url()
        if webhook_url and config.is_configured():
            self.notifier = create_notifier(
                config.notification_type,
                webhook_url
            )

    def check_feed(self, service_id: str, feed_config: FeedConfig) -> None:
        """
        Check a single RSS feed for updates.

        Args:
            service_id: Unique identifier for the service
            feed_config: Configuration for the RSS feed
        """
        logger.info(f"Checking {feed_config.name}...")

        # Parse the feed
        feed = self.parser.parse_feed(feed_config.url)
        if not feed:
            logger.error(f"Failed to parse feed for {feed_config.name}")
            return

        # Extract latest entry
        entry = self.parser.extract_latest_entry(feed)
        if not entry:
            logger.warning(f"No entries found for {feed_config.name}")
            return

        # Check if this is a new entry
        last_seen_id = self.state_manager.get_last_id(service_id)

        if last_seen_id != entry.entry_id:
            logger.info(f"New status update for {feed_config.name}")

            # Check if this is an active incident
            if self.filter.is_active_incident(entry.title, entry.description):
                logger.warning(f"Active incident detected for {feed_config.name}")
                self._send_notification(feed_config, entry)
            else:
                logger.info(
                    f"Status update is a resolution/normal status - "
                    f"skipping notification"
                )

            # Update state regardless of notification (avoid reprocessing)
            self.state_manager.update_service(
                service_id,
                entry.entry_id,
                entry.title
            )
        else:
            logger.debug(f"No new updates for {feed_config.name}")

    def _send_notification(
        self,
        feed_config: FeedConfig,
        entry
    ) -> None:
        """
        Send notification for an incident.

        Args:
            feed_config: Configuration for the feed
            entry: The feed entry to notify about
        """
        if not self.notifier:
            logger.warning("Notifier not configured, skipping notification")
            return

        success = self.notifier.send(
            service_name=feed_config.name,
            title=entry.title,
            description=entry.description,
            link=entry.link,
            color=feed_config.color
        )

        if success:
            logger.info(f"Notification sent for {feed_config.name}")
        else:
            logger.error(f"Failed to send notification for {feed_config.name}")

    def run_check_cycle(self) -> None:
        """Run a single check cycle for all feeds"""
        logger.info(
            f"Check started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        for service_id, feed_config in FEEDS.items():
            try:
                self.check_feed(service_id, feed_config)
            except Exception as e:
                logger.error(
                    f"Unexpected error checking {feed_config.name}: {e}",
                    exc_info=True
                )

        # Save state after all checks
        self.state_manager.save()
        logger.info(
            f"Check cycle completed. Next check in {self.config.check_interval}s"
        )

    def run(self) -> None:
        """Main monitoring loop"""
        logger.info("🚀 LLM Status Monitor Started")
        logger.info(f"⏱️  Check interval: {self.config.check_interval} seconds")
        logger.info(
            f"📊 Monitoring: {', '.join([f.name for f in FEEDS.values()])}"
        )
        logger.info(f"📢 Notification type: {self.config.notification_type}")

        # Check if notifications are configured
        if not self.config.is_configured():
            logger.warning(
                f"{self.config.notification_type.upper()} webhook not configured. "
                f"Notifications disabled."
            )
            logger.warning(
                f"Set {self.config.notification_type.upper()}_WEBHOOK_URL in .env"
            )

        # Load initial state
        self.state_manager.load()

        try:
            while True:
                self.run_check_cycle()
                time.sleep(self.config.check_interval)

        except KeyboardInterrupt:
            logger.info("Monitor stopped by user")
            self.state_manager.save()
        except Exception as e:
            logger.error(f"Unexpected error in monitoring loop: {e}", exc_info=True)
            self.state_manager.save()
            raise

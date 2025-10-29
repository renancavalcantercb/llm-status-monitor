"""
RSS feed parsing for status pages
"""

import re
import logging
import feedparser
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FeedEntry:
    """Represents a parsed RSS feed entry"""
    entry_id: str
    title: str
    description: str
    link: str
    published: Optional[str] = None


class FeedParser:
    """Parser for RSS status feeds"""

    @staticmethod
    def parse_feed(url: str) -> Optional[feedparser.FeedParserDict]:
        """
        Parse an RSS feed from a URL.

        Args:
            url: The RSS feed URL to parse

        Returns:
            Parsed feed object, or None if parsing failed
        """
        try:
            feed = feedparser.parse(url)

            if feed.bozo:
                logger.warning(f"Feed parsing warning for {url}")
                if hasattr(feed, 'bozo_exception'):
                    logger.warning(f"Parse exception: {feed.bozo_exception}")

            if not feed.entries:
                logger.warning(f"No entries found in feed: {url}")
                return None

            return feed

        except Exception as e:
            logger.error(f"Failed to parse feed {url}: {e}")
            return None

    @staticmethod
    def extract_latest_entry(feed: feedparser.FeedParserDict) -> Optional[FeedEntry]:
        """
        Extract the latest entry from a parsed feed.

        Args:
            feed: Parsed feed object from feedparser

        Returns:
            FeedEntry object with latest entry data, or None if no entries
        """
        if not feed.entries:
            return None

        latest = feed.entries[0]

        # Get entry ID (prefer id, fallback to link)
        entry_id = latest.get('id', latest.get('link', ''))
        if not entry_id:
            logger.warning("Feed entry has no ID or link")
            return None

        # Get title
        title = latest.get('title', 'Status Update')

        # Get description (try summary first, then description)
        description = latest.get('summary', latest.get('description', ''))

        # Clean HTML tags from description
        if description:
            description = FeedParser._clean_html(description)

        # Get link
        link = latest.get('link', '')

        # Get published date
        published = latest.get('published', latest.get('updated'))

        return FeedEntry(
            entry_id=entry_id,
            title=title,
            description=description,
            link=link,
            published=published
        )

    @staticmethod
    def _clean_html(text: str) -> str:
        """
        Remove HTML tags from text.

        Args:
            text: Text potentially containing HTML tags

        Returns:
            Cleaned text without HTML tags
        """
        return re.sub('<[^<]+?>', '', text).strip()

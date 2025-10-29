"""
Incident filtering logic for status updates
"""

import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class IncidentFilter:
    """Filter to determine if status updates represent active incidents"""

    # Keywords indicating resolved/normal status
    RESOLVED_KEYWORDS: Tuple[str, ...] = (
        'resolved',
        'recovered',
        'fixed',
        'completed',
        'restored',
        'all services operational',
        'all impacted services have now fully recovered',
        'post-mortem',
        'has been resolved',
        'issue has been fixed'
    )

    # Keywords indicating active incidents
    INCIDENT_KEYWORDS: Tuple[str, ...] = (
        'investigating',
        'identified',
        'monitoring',
        'degraded',
        'outage',
        'down',
        'unavailable',
        'elevated error',
        'high error rate',
        'partial outage',
        'major outage',
        'service disruption',
        'experiencing issues',
        'incident',
        'problem',
        'failing',
        'not loading',
        'broken'
    )

    @classmethod
    def is_active_incident(cls, title: str, description: str) -> bool:
        """
        Determine if an RSS entry represents an active incident/problem.

        Returns True only for active incidents that should trigger notifications.
        Returns False for resolved issues, completed maintenance, or normal status.

        Args:
            title: The title of the status update
            description: The description/summary of the status update

        Returns:
            True if this is an active incident, False otherwise
        """
        # Combine title and description for analysis
        text = f"{title} {description}".lower()

        # Check for resolved/normal indicators first
        for keyword in cls.RESOLVED_KEYWORDS:
            if keyword in text:
                logger.debug(
                    f"Status update marked as resolved (keyword: '{keyword}')"
                )
                return False

        # Check for active incident indicators
        for keyword in cls.INCIDENT_KEYWORDS:
            if keyword in text:
                logger.debug(
                    f"Active incident detected (keyword: '{keyword}')"
                )
                return True

        # Default: don't notify if unsure
        logger.debug("No clear incident markers found, defaulting to skip")
        return False

"""
Test suite for incident filtering logic
"""

import pytest
from llm_monitor.filters import IncidentFilter


class TestIncidentFilter:
    """Tests for the IncidentFilter class"""

    @pytest.mark.parametrize("title,description,expected,reason", [
        # ACTIVE INCIDENTS (should return True)
        (
            "Elevated errors for requests to Claude 4.5 Haiku",
            "Service disruption affecting Claude 4.5 Haiku. A fix has been implemented and we are monitoring the results.",
            True,
            "Contains 'elevated errors' and 'monitoring'"
        ),
        (
            "Elevated errors with uploading files to claude.ai",
            "File upload functionality issues. Investigating the problem.",
            True,
            "Contains 'elevated errors' and 'investigating'"
        ),
        (
            "High error rates on gpt-4o-audio-preview",
            "Audio component experiencing elevated errors. Issue identified.",
            True,
            "Contains 'high error rates' and 'identified'"
        ),
        (
            "API service degraded performance",
            "Users may experience slower response times. We are investigating.",
            True,
            "Contains 'degraded' and 'investigating'"
        ),
        (
            "Members Page in Admin Settings not loading",
            "The members page is currently unavailable. We are working on a fix.",
            True,
            "Contains 'not loading' and 'unavailable'"
        ),

        # RESOLVED INCIDENTS (should return False)
        (
            "Elevated errors for requests to Claude 4.5 Sonnet",
            "The issue has been identified and a fix has been implemented. All services are now operational. Resolved.",
            False,
            "Contains 'resolved' and 'operational'"
        ),
        (
            "High error rates on gpt-4o-audio-preview",
            "Audio component has fully recovered. All impacted services have now fully recovered.",
            False,
            "Contains 'recovered'"
        ),
        (
            "API latency issues",
            "The latency issue has been fixed and services are restored to normal.",
            False,
            "Contains 'fixed' and 'restored'"
        ),
        (
            "Scheduled Maintenance Completed",
            "The scheduled maintenance has completed successfully. All systems operational.",
            False,
            "Contains 'completed'"
        ),
        (
            "Post-mortem: API Outage on Oct 25",
            "Analysis of the outage that occurred last week.",
            False,
            "Post-mortem (historical)"
        )
    ])
    def test_is_active_incident(self, title, description, expected, reason):
        """Test incident detection with various real-world scenarios"""
        result = IncidentFilter.is_active_incident(title, description)
        assert result == expected, f"Failed: {reason}"

    def test_empty_inputs(self):
        """Test with empty title and description"""
        assert IncidentFilter.is_active_incident("", "") is False

    def test_case_insensitivity(self):
        """Test that keyword matching is case-insensitive"""
        assert IncidentFilter.is_active_incident(
            "INVESTIGATING OUTAGE",
            "Service is DOWN"
        ) is True

        assert IncidentFilter.is_active_incident(
            "Issue RESOLVED",
            "Service RECOVERED"
        ) is False

    def test_resolved_takes_precedence(self):
        """Test that resolved keywords take precedence over incident keywords"""
        # Even if incident keywords are present, resolved should win
        result = IncidentFilter.is_active_incident(
            "Investigating issue - now resolved",
            "The outage has been resolved and service is operational"
        )
        assert result is False

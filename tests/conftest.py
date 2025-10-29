"""
Pytest configuration and shared fixtures
"""

import pytest
import os
from unittest.mock import patch


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """
    Clean environment variables before each test.
    This prevents tests from being affected by actual .env file.
    """
    # Mock load_dotenv to prevent loading .env file in tests
    with patch('llm_monitor.config.load_dotenv'):
        # Clear common env vars
        env_vars = [
            'NOTIFICATION_TYPE',
            'DISCORD_WEBHOOK_URL',
            'SLACK_WEBHOOK_URL',
            'CHECK_INTERVAL',
            'STATE_FILE',
            'LOG_LEVEL'
        ]

        for var in env_vars:
            monkeypatch.delenv(var, raising=False)

        # Set safe defaults
        monkeypatch.setenv('NOTIFICATION_TYPE', 'discord')

        yield

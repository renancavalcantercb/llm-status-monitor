"""
Test suite for configuration management
"""

import pytest
import os
from pathlib import Path
from llm_monitor.config import Config, FeedConfig, FEEDS


class TestConfig:
    """Tests for Config class"""

    def test_feed_config_dataclass(self):
        """Test FeedConfig creation"""
        feed = FeedConfig(
            name="Test Service",
            url="https://example.com/rss",
            color=0xFF0000
        )
        assert feed.name == "Test Service"
        assert feed.url == "https://example.com/rss"
        assert feed.color == 0xFF0000

    def test_feeds_configuration(self):
        """Test that default FEEDS are properly configured"""
        assert 'claude' in FEEDS
        assert 'chatgpt' in FEEDS
        assert FEEDS['claude'].name == 'Anthropic (Claude)'
        assert FEEDS['chatgpt'].name == 'OpenAI (ChatGPT)'

    def test_is_configured_discord(self, monkeypatch):
        """Test is_configured for Discord"""
        monkeypatch.setenv('NOTIFICATION_TYPE', 'discord')
        monkeypatch.setenv('DISCORD_WEBHOOK_URL', 'https://discord.com/webhook')

        config = Config.from_env()
        assert config.is_configured() is True

    def test_is_configured_slack(self, monkeypatch):
        """Test is_configured for Slack"""
        monkeypatch.setenv('NOTIFICATION_TYPE', 'slack')
        monkeypatch.setenv('SLACK_WEBHOOK_URL', 'https://hooks.slack.com/webhook')

        config = Config.from_env()
        assert config.is_configured() is True

    def test_is_not_configured(self, monkeypatch):
        """Test is_configured when webhook is missing"""
        # Explicitly clear all webhook env vars
        monkeypatch.delenv('DISCORD_WEBHOOK_URL', raising=False)
        monkeypatch.delenv('SLACK_WEBHOOK_URL', raising=False)
        monkeypatch.setenv('NOTIFICATION_TYPE', 'discord')

        config = Config.from_env()
        assert config.is_configured() is False

    def test_get_webhook_url_discord(self, monkeypatch):
        """Test get_webhook_url for Discord"""
        webhook = 'https://discord.com/webhook'
        monkeypatch.setenv('NOTIFICATION_TYPE', 'discord')
        monkeypatch.setenv('DISCORD_WEBHOOK_URL', webhook)

        config = Config.from_env()
        assert config.get_webhook_url() == webhook

    def test_get_webhook_url_slack(self, monkeypatch):
        """Test get_webhook_url for Slack"""
        webhook = 'https://hooks.slack.com/webhook'
        monkeypatch.setenv('NOTIFICATION_TYPE', 'slack')
        monkeypatch.setenv('SLACK_WEBHOOK_URL', webhook)

        config = Config.from_env()
        assert config.get_webhook_url() == webhook

    def test_invalid_notification_type(self, monkeypatch):
        """Test that invalid notification type raises ValueError"""
        monkeypatch.setenv('NOTIFICATION_TYPE', 'invalid')

        with pytest.raises(ValueError, match="Invalid NOTIFICATION_TYPE"):
            Config.from_env()

    def test_default_check_interval(self, monkeypatch):
        """Test default check interval"""
        monkeypatch.setenv('NOTIFICATION_TYPE', 'discord')
        monkeypatch.delenv('CHECK_INTERVAL', raising=False)

        config = Config.from_env()
        assert config.check_interval == 300  # Default 5 minutes

    def test_custom_check_interval(self, monkeypatch):
        """Test custom check interval"""
        monkeypatch.setenv('NOTIFICATION_TYPE', 'discord')
        monkeypatch.setenv('CHECK_INTERVAL', '600')

        config = Config.from_env()
        assert config.check_interval == 600

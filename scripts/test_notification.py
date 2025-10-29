#!/usr/bin/env python3
"""
Test notification script - Send a test message to Discord or Slack
"""

import os
from dotenv import load_dotenv
from monitor import send_notification, NOTIFICATION_TYPE, DISCORD_WEBHOOK, SLACK_WEBHOOK

load_dotenv()

def test_notification():
    """Send a test notification to configured service"""
    print("🧪 Testing notification system...")
    print(f"📢 Notification type: {NOTIFICATION_TYPE}")

    # Check configuration
    if NOTIFICATION_TYPE == 'discord':
        if not DISCORD_WEBHOOK:
            print("❌ DISCORD_WEBHOOK_URL not configured in .env")
            return False
        print(f"✓ Discord webhook configured")
    elif NOTIFICATION_TYPE == 'slack':
        if not SLACK_WEBHOOK:
            print("❌ SLACK_WEBHOOK_URL not configured in .env")
            return False
        print(f"✓ Slack webhook configured")
    else:
        print(f"❌ Invalid NOTIFICATION_TYPE: {NOTIFICATION_TYPE}")
        print("   Valid options: 'discord' or 'slack'")
        return False

    print("\n📤 Sending test notification...")

    # Send test notification
    success = send_notification(
        service_name="Test Service",
        title="Test Notification - System Working",
        description="This is a test notification from LLM Status Monitor. If you see this message, your webhook configuration is working correctly!",
        link="https://github.com",
        color=0x00FF00  # Green color for test
    )

    if success:
        print("\n✅ Test notification sent successfully!")
        print(f"   Check your {NOTIFICATION_TYPE.title()} channel for the message.")
        return True
    else:
        print("\n❌ Failed to send test notification")
        print(f"   Check your {NOTIFICATION_TYPE.upper()}_WEBHOOK_URL in .env")
        return False

if __name__ == '__main__':
    test_notification()

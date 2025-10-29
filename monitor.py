#!/usr/bin/env python3
"""
LLM Status Monitor - Monitor status pages for Claude and ChatGPT
"""

import feedparser
import requests
import json
import time
import os
import re
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
NOTIFICATION_TYPE = os.getenv('NOTIFICATION_TYPE', 'discord').lower()
DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK_URL')
SLACK_WEBHOOK = os.getenv('SLACK_WEBHOOK_URL')
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 300))
STATE_FILE = Path('data/state.json')

# RSS Feeds
FEEDS = {
    'claude': {
        'name': 'Anthropic (Claude)',
        'url': 'https://status.claude.com/history.rss',
        'color': 0xD97757  # Orange/brown color for Claude
    },
    'chatgpt': {
        'name': 'OpenAI (ChatGPT)',
        'url': 'https://status.openai.com/history.rss',
        'color': 0x10A37F  # Green color for OpenAI
    }
}


def is_active_incident(title, description):
    """
    Determine if an RSS entry represents an active incident/problem.
    Returns True only for active incidents that should trigger notifications.
    Returns False for resolved issues, completed maintenance, or normal status.
    """
    # Combine title and description for analysis
    text = f"{title} {description}".lower()

    # RESOLVED/NORMAL indicators - if present, NOT an active incident
    resolved_keywords = [
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
    ]

    for keyword in resolved_keywords:
        if keyword in text:
            return False

    # ACTIVE INCIDENT indicators
    incident_keywords = [
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
    ]

    for keyword in incident_keywords:
        if keyword in text:
            return True

    # Default: don't notify if unsure
    return False


def load_state():
    """Load previous state from file"""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_state(state):
    """Save current state to file"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)


def send_discord_notification(service_name, title, description, link, color):
    """Send notification to Discord webhook"""
    if not DISCORD_WEBHOOK:
        print("⚠️  Discord webhook not configured")
        return False

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

    payload = {
        "embeds": [embed]
    }

    try:
        response = requests.post(DISCORD_WEBHOOK, json=payload)
        response.raise_for_status()
        print(f"✅ Discord notification sent for {service_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to send Discord notification: {e}")
        return False


def send_slack_notification(service_name, title, description, link, color):
    """Send notification to Slack webhook"""
    if not SLACK_WEBHOOK:
        print("⚠️  Slack webhook not configured")
        return False

    # Convert hex color to Slack's color format
    color_map = {
        0xD97757: '#D97757',  # Claude orange/brown
        0x10A37F: '#10A37F',  # OpenAI green
    }
    slack_color = color_map.get(color, '#FF0000')  # Default to red

    # Build Slack message with Block Kit
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
        response = requests.post(SLACK_WEBHOOK, json=payload)
        response.raise_for_status()
        print(f"✅ Slack notification sent for {service_name}")
        return True
    except Exception as e:
        print(f"❌ Failed to send Slack notification: {e}")
        return False


def send_notification(service_name, title, description, link, color):
    """Send notification to configured service (Discord or Slack)"""
    if NOTIFICATION_TYPE == 'slack':
        return send_slack_notification(service_name, title, description, link, color)
    elif NOTIFICATION_TYPE == 'discord':
        return send_discord_notification(service_name, title, description, link, color)
    else:
        print(f"⚠️  Unknown notification type: {NOTIFICATION_TYPE}")
        print(f"   Valid options: 'discord' or 'slack'")
        return False


def check_feed(service_id, feed_config, state):
    """Check a single RSS feed for updates"""
    print(f"🔍 Checking {feed_config['name']}...")

    try:
        feed = feedparser.parse(feed_config['url'])

        if feed.bozo:
            print(f"⚠️  Feed parsing warning for {feed_config['name']}")

        if not feed.entries:
            print(f"ℹ️  No entries found in {feed_config['name']}")
            return state

        # Get the most recent entry
        latest_entry = feed.entries[0]
        latest_id = latest_entry.get('id', latest_entry.get('link', ''))

        # Check if this is a new entry
        last_seen_id = state.get(service_id, {}).get('last_id')

        if last_seen_id != latest_id:
            print(f"🆕 New status update for {feed_config['name']}")

            # Extract entry details
            title = latest_entry.get('title', 'Status Update')
            description = latest_entry.get('summary', latest_entry.get('description', ''))
            link = latest_entry.get('link', feed_config['url'])

            # Clean HTML tags from description if present
            if description:
                description = re.sub('<[^<]+?>', '', description).strip()

            # Check if this is an active incident (not a resolution)
            if is_active_incident(title, description):
                print(f"🚨 Active incident detected - sending notification")
                send_notification(
                    feed_config['name'],
                    title,
                    description,
                    link,
                    feed_config['color']
                )
            else:
                print(f"✅ Status update is a resolution/normal status - skipping notification")

            # Update state regardless of notification (to avoid reprocessing)
            state[service_id] = {
                'last_id': latest_id,
                'last_title': title,
                'last_checked': datetime.now().isoformat()
            }
        else:
            print(f"✓ No new updates for {feed_config['name']}")

        return state

    except Exception as e:
        print(f"❌ Error checking {feed_config['name']}: {e}")
        return state


def monitor():
    """Main monitoring loop"""
    print("🚀 LLM Status Monitor Started")
    print(f"⏱️  Check interval: {CHECK_INTERVAL} seconds")
    print(f"📊 Monitoring: {', '.join([f['name'] for f in FEEDS.values()])}")
    print(f"📢 Notification type: {NOTIFICATION_TYPE}")
    print("-" * 60)

    # Check if notifications are configured
    webhook_configured = (
        (NOTIFICATION_TYPE == 'discord' and DISCORD_WEBHOOK) or
        (NOTIFICATION_TYPE == 'slack' and SLACK_WEBHOOK)
    )

    if not webhook_configured:
        print(f"⚠️  WARNING: {NOTIFICATION_TYPE.upper()} webhook not configured. Notifications disabled.")
        print("   Copy .env.example to .env and configure your webhook URL.")
        print(f"   Required variable: {NOTIFICATION_TYPE.upper()}_WEBHOOK_URL")
        print("-" * 60)

    state = load_state()

    try:
        while True:
            print(f"\n🔄 Check started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            for service_id, feed_config in FEEDS.items():
                state = check_feed(service_id, feed_config, state)

            save_state(state)

            print(f"💾 State saved. Next check in {CHECK_INTERVAL} seconds...")
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\n\n👋 Monitor stopped by user")
        save_state(state)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        save_state(state)
        raise


if __name__ == '__main__':
    monitor()

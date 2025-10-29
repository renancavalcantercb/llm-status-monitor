#!/usr/bin/env python3
"""
Test script to verify RSS feeds are accessible and parseable
"""

import feedparser
import sys

FEEDS = {
    'Anthropic (Claude)': 'https://status.claude.com/history.rss',
    'OpenAI (ChatGPT)': 'https://status.openai.com/history.rss'
}

def test_feed(name, url):
    """Test a single RSS feed"""
    print(f"\n{'='*60}")
    print(f"Testing: {name}")
    print(f"URL: {url}")
    print('='*60)

    try:
        feed = feedparser.parse(url)

        if feed.bozo:
            print(f"⚠️  Warning: Feed has parsing issues")
            if hasattr(feed, 'bozo_exception'):
                print(f"   Exception: {feed.bozo_exception}")

        if not feed.entries:
            print("❌ No entries found in feed")
            return False

        print(f"✅ Feed parsed successfully")
        print(f"📊 Total entries: {len(feed.entries)}")

        # Show latest entry
        latest = feed.entries[0]
        print(f"\n📰 Latest Entry:")
        print(f"   Title: {latest.get('title', 'N/A')}")
        print(f"   Published: {latest.get('published', 'N/A')}")
        print(f"   Link: {latest.get('link', 'N/A')}")

        # Show ID/GUID
        entry_id = latest.get('id', latest.get('link', 'N/A'))
        print(f"   ID: {entry_id}")

        # Show summary (truncated)
        summary = latest.get('summary', latest.get('description', 'No summary'))
        if len(summary) > 200:
            summary = summary[:200] + '...'
        print(f"   Summary: {summary}")

        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🧪 LLM Status Monitor - Feed Test")
    print("Testing RSS feed accessibility and parsing...\n")

    results = {}
    for name, url in FEEDS.items():
        results[name] = test_feed(name, url)

    # Summary
    print(f"\n{'='*60}")
    print("📋 SUMMARY")
    print('='*60)

    all_passed = True
    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False

    if all_passed:
        print("\n🎉 All feeds are working correctly!")
        return 0
    else:
        print("\n⚠️  Some feeds have issues. Check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())

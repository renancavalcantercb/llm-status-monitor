#!/usr/bin/env python3
"""
Test script to validate the incident filter logic
"""

# Import the filter function from monitor.py
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from monitor import is_active_incident


# Test cases from real RSS feeds
test_cases = [
    # ACTIVE INCIDENTS (should return True)
    {
        "title": "Elevated errors for requests to Claude 4.5 Haiku",
        "description": "Service disruption affecting Claude 4.5 Haiku. A fix has been implemented and we are monitoring the results.",
        "expected": True,
        "reason": "Contains 'elevated errors' and 'monitoring'"
    },
    {
        "title": "Elevated errors with uploading files to claude.ai",
        "description": "File upload functionality issues. Investigating the problem.",
        "expected": True,
        "reason": "Contains 'elevated errors' and 'investigating'"
    },
    {
        "title": "High error rates on gpt-4o-audio-preview",
        "description": "Audio component experiencing elevated errors. Issue identified.",
        "expected": True,
        "reason": "Contains 'high error rates' and 'identified'"
    },
    {
        "title": "API service degraded performance",
        "description": "Users may experience slower response times. We are investigating.",
        "expected": True,
        "reason": "Contains 'degraded' and 'investigating'"
    },
    {
        "title": "Members Page in Admin Settings not loading",
        "description": "The members page is currently unavailable. We are working on a fix.",
        "expected": True,
        "reason": "Contains 'not loading' and 'unavailable'"
    },

    # RESOLVED INCIDENTS (should return False)
    {
        "title": "Elevated errors for requests to Claude 4.5 Sonnet",
        "description": "The issue has been identified and a fix has been implemented. All services are now operational. Resolved.",
        "expected": False,
        "reason": "Contains 'resolved' and 'operational'"
    },
    {
        "title": "High error rates on gpt-4o-audio-preview",
        "description": "Audio component has fully recovered. All impacted services have now fully recovered.",
        "expected": False,
        "reason": "Contains 'recovered'"
    },
    {
        "title": "API latency issues",
        "description": "The latency issue has been fixed and services are restored to normal.",
        "expected": False,
        "reason": "Contains 'fixed' and 'restored'"
    },
    {
        "title": "Scheduled Maintenance Completed",
        "description": "The scheduled maintenance has completed successfully. All systems operational.",
        "expected": False,
        "reason": "Contains 'completed'"
    },
    {
        "title": "Post-mortem: API Outage on Oct 25",
        "description": "Analysis of the outage that occurred last week.",
        "expected": False,
        "reason": "Post-mortem (historical)"
    }
]


def run_tests():
    """Run all test cases and report results"""
    print("🧪 Testing Incident Filter Logic")
    print("=" * 70)

    passed = 0
    failed = 0

    for i, test in enumerate(test_cases, 1):
        title = test["title"]
        description = test["description"]
        expected = test["expected"]
        reason = test["reason"]

        result = is_active_incident(title, description)
        status = "✅ PASS" if result == expected else "❌ FAIL"

        if result == expected:
            passed += 1
        else:
            failed += 1

        print(f"\n{i}. {status}")
        print(f"   Title: {title}")
        print(f"   Expected: {'NOTIFY' if expected else 'SKIP'}")
        print(f"   Got: {'NOTIFY' if result else 'SKIP'}")
        print(f"   Reason: {reason}")

    # Summary
    print("\n" + "=" * 70)
    print(f"📊 RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")

    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())

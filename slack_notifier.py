#!/usr/bin/env python3
"""
Slack Notifier for Gaming Stock Tracker
Sends daily summaries to Slack channel
"""

import json
import os
import sys
from datetime import datetime, timedelta
import requests

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Slack webhook URL (set via environment variable for security)
SLACK_WEBHOOK_URL = os.environ.get('SLACK_WEBHOOK_URL', '')

# Configuration
DASHBOARD_URL = 'https://adamware-creator.github.io/gaming-stock-tracker/'
DATA_FILE = 'stock_tracker_history.json'

GAMING_COMPANIES = {
    'DKNG': 'DraftKings',
    'FLUT': 'Flutter Entertainment',
    'CZR': 'Caesars Entertainment',
    'MGM': 'MGM Resorts',
    'PENN': 'Penn Entertainment',
    'RSI': 'Rush Street Interactive',
    'BALY': "Bally's Corporation"
}


def load_latest_data():
    """Load the most recent trading day's data"""
    if not os.path.exists(DATA_FILE):
        return None

    with open(DATA_FILE, 'r') as f:
        data = json.load(f)

    if not data.get('records'):
        return None

    # Get the most recent record
    records = sorted(data['records'], key=lambda x: x['date'], reverse=True)
    return records[0] if records else None


def format_slack_message(record):
    """Format the data into a Slack message"""
    if not record:
        return {
            "text": "⚠️ No stock data available to report."
        }

    date_display = record.get('date_display', 'Unknown Date')
    benchmark_data = record.get('benchmark', {})
    benchmark_change = benchmark_data.get('pct_change', 0) if benchmark_data else 0
    material_changes = record.get('material_changes', [])
    companies = record.get('companies', {})

    # Build message blocks
    blocks = []

    # Header
    blocks.append({
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": f"📊 Gaming Stock Update - {date_display}",
            "emoji": True
        }
    })

    # NASDAQ Benchmark
    benchmark_emoji = "🟢" if benchmark_change >= 0 else "🔴"
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"{benchmark_emoji} *NASDAQ:* {benchmark_change:+.2f}%"
        }
    })

    blocks.append({"type": "divider"})

    # Material Changes Section
    if material_changes:
        changes_header = f"*🚨 Material Changes (±2%):* {len(material_changes)}\n"
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": changes_header
            }
        })
        blocks.append({"type": "divider"})

        # Show each material change with explanation
        for change in material_changes:
            ticker = change['ticker']
            name = change['name']
            company_info = companies.get(ticker, {})
            # Handle nested data structure
            data = company_info.get('data', company_info)
            pct_change = data.get('pct_change', 0)
            current_price = data.get('current_price', 0)

            emoji = "🟢" if pct_change > 0 else "🔴"

            # Build change text
            change_text = f"{emoji} *{ticker}* ({name})\n"
            change_text += f"`{pct_change:+.2f}%` | ${current_price:.2f}\n"

            # Add news summary if available
            news = change.get('news', {})
            summary = news.get('summary', '')
            if summary:
                change_text += f"\n_{summary}_"

            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": change_text
                }
            })

        blocks.append({"type": "divider"})
    else:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*No material changes today* (all movements < ±2%)"
            }
        })
        blocks.append({"type": "divider"})

    # Dashboard Link
    blocks.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"📊 <{DASHBOARD_URL}|View Full Dashboard>"
        }
    })

    return {
        "blocks": blocks,
        "text": f"Gaming Stock Update - {date_display}"  # Fallback text
    }


def send_to_slack(message):
    """Send message to Slack via webhook"""
    if not SLACK_WEBHOOK_URL:
        print("ERROR: SLACK_WEBHOOK_URL environment variable not set!")
        print("\nSet it with:")
        print("  export SLACK_WEBHOOK_URL='your-webhook-url'")
        print("  or")
        print("  set SLACK_WEBHOOK_URL=your-webhook-url  (Windows)")
        return False

    try:
        # Disable SSL warnings for Windows environments
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=message,
            headers={'Content-Type': 'application/json'},
            verify=False  # Disable SSL verification for Windows SSL certificate issues
        )

        if response.status_code == 200:
            print("✅ Message sent to Slack successfully!")
            return True
        else:
            print(f"❌ Failed to send message. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error sending to Slack: {e}")
        return False


def main():
    """Main function"""
    print("=" * 70)
    print("SLACK NOTIFIER - Gaming Stock Tracker")
    print("=" * 70)
    print()

    # Load latest data
    print("Loading latest stock data...")
    record = load_latest_data()

    if not record:
        print("❌ No data found in stock_tracker_history.json")
        sys.exit(1)

    print(f"✅ Loaded data for: {record.get('date_display', 'Unknown')}")
    print()

    # Format message
    print("Formatting Slack message...")
    message = format_slack_message(record)
    print("✅ Message formatted")
    print()

    # Send to Slack
    print("Sending to Slack...")
    success = send_to_slack(message)

    if success:
        print()
        print("=" * 70)
        print("✅ Daily update sent successfully!")
        print("=" * 70)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()

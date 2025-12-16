#!/usr/bin/env python3
"""
Simple wrapper to send Slack updates
Loads webhook URL from .env file or environment variable
"""

import os
import sys

# Try to load from .env file if it exists
if os.path.exists('.env'):
    print("Loading configuration from .env file...")
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Check if webhook URL is set
if not os.environ.get('SLACK_WEBHOOK_URL'):
    print("❌ ERROR: SLACK_WEBHOOK_URL not found!")
    print()
    print("Please create a .env file with your Slack webhook URL:")
    print("  1. Copy .env.example to .env")
    print("  2. Edit .env and add your webhook URL")
    print()
    print("Or set it as an environment variable:")
    print("  Windows: set SLACK_WEBHOOK_URL=your-url")
    print("  Mac/Linux: export SLACK_WEBHOOK_URL=your-url")
    sys.exit(1)

# Import and run the notifier
from slack_notifier import main

if __name__ == '__main__':
    main()

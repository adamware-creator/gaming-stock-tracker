#!/usr/bin/env python3
"""
Automatically fetch and generate earnings call summaries
This script is designed to be run within Claude Code environment
"""
import json

def load_earnings_data():
    """Load earnings data"""
    with open('earnings_data.json', 'r') as f:
        return json.load(f)

def save_earnings_data(data):
    """Save earnings data"""
    with open('earnings_data.json', 'w') as f:
        json.dump(data, f, indent=2)

# List of earnings calls that need summaries
EARNINGS_CALLS_TO_FETCH = [
    ('DKNG', 'DraftKings', 'Q3 2024'),
    ('DKNG', 'DraftKings', 'Q4 2024'),
    ('DKNG', 'DraftKings', 'Q1 2025'),
    ('DKNG', 'DraftKings', 'Q2 2025'),
    ('DKNG', 'DraftKings', 'Q3 2025'),
]

if __name__ == "__main__":
    print("This script should be run by Claude Code to fetch earnings summaries automatically.")
    print("Claude can use WebSearch to find and summarize earnings calls.")
    print("\nUse the main dashboard generation instead, which will prompt Claude to fetch missing summaries.")

#!/usr/bin/env python3
"""
Automatically fetch earnings call summaries using web search
"""
import json
import os

# Note: This script requires access to WebSearch which is only available in Claude Code
# When run standalone, it will print instructions for manual updates

def load_earnings_data():
    """Load earnings data"""
    with open('earnings_data.json', 'r') as f:
        return json.load(f)

def save_earnings_data(data):
    """Save earnings data"""
    with open('earnings_data.json', 'w') as f:
        json.dump(data, f, indent=2)

def generate_earnings_summary_prompt(company_name, ticker, quarter):
    """Generate a prompt for summarizing an earnings call"""
    return f"""Give me a comprehensive one-paragraph summary of {company_name} ({ticker}) {quarter} earnings call including:
1. Key financial metrics (revenue, earnings, YoY growth)
2. Management presentation highlights (CEO/CFO prepared remarks on strategy, performance, guidance)
3. Investor Q&A topics (analyst questions, management responses, main concerns/opportunities discussed)
4. Market reaction (stock price movement post-earnings, analyst sentiment)

Keep it dense with specific numbers and quotes where possible. Focus on what matters most to investors."""

def list_quarters_needing_summaries():
    """List all quarters that need earnings call summaries"""
    earnings_data = load_earnings_data()

    print("\nQuarters needing earnings call summaries:")
    print("=" * 70)

    for ticker, company_data in earnings_data['companies'].items():
        name = company_data.get('name', ticker)
        quarters = company_data.get('quarters', {})

        needs_summary = []
        for quarter, data in sorted(quarters.items()):
            if not data.get('presentation_summary') and data.get('revenue'):
                needs_summary.append(quarter)

        if needs_summary:
            print(f"\n{name} ({ticker}):")
            for quarter in needs_summary:
                print(f"  - {quarter}")
                prompt = generate_earnings_summary_prompt(name, ticker, quarter)
                print(f"    Search: \"{name} {ticker} {quarter} earnings call\"")

if __name__ == "__main__":
    print("Earnings Call Summary Fetcher")
    print("=" * 70)
    print("\nThis script identifies quarters that need earnings call summaries.")
    print("To add summaries automatically, use Claude Code's WebSearch capability.")
    print("\nAlternatively, you can:")
    print("1. Search for the earnings call transcript")
    print("2. Ask an AI to summarize it")
    print("3. Add it using: python earnings_tracker.py TICKER QUARTER \"Summary\"")

    list_quarters_needing_summaries()

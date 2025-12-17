#!/usr/bin/env python3
"""
All-in-one daily update script
Fetches stock data, researches news, and updates dashboard automatically

NOTE: This script generates placeholder news summaries that require manual research.
After running this script, you'll need to research and update the news narratives
with actual market catalysts and context.
"""
import sys
import json
from datetime import datetime, timedelta

# Import the tracker functions
sys.path.insert(0, '.')
from gaming_stock_tracker_v3 import (
    analyze_single_day,
    load_historical_data,
    save_historical_data,
    generate_html_dashboard,
    GAMING_COMPANIES
)

def research_news_for_material_change(ticker, name, pct_change, date_display, current_price, open_price):
    """
    Research news for a material change

    NOTE: This function currently creates structured placeholders.
    Manual research is required to populate with actual news catalysts.

    To get real news narratives, you'll need to:
    1. Run this script to fetch stock data
    2. Manually research each material change
    3. Update the JSON with actual news context
    4. Regenerate the dashboard
    """
    direction = "up" if pct_change > 0 else "down"
    direction_verb = "rose" if pct_change > 0 else "fell"

    # Build search query for manual research
    search_query = f"{name} {ticker} stock {direction} {date_display}"

    print(f"  {ticker} {pct_change:+.2f}% - Search: {search_query}")

    # Create placeholder with correct direction and percentage
    summary = f"{name} {direction_verb} {pct_change:+.1f}% on {date_display}. [PLACEHOLDER: Research needed for catalysts - analyst actions, earnings news, market events, sector trends, or company announcements]"

    return {
        'search_query': search_query,
        'summary': summary,
        'needs_manual_lookup': True
    }

def update_yesterday():
    """
    Complete workflow: fetch data, research news, update dashboard
    """
    print("=" * 70)
    print("DAILY UPDATE - Automated Stock Data + News Research")
    print("=" * 70)

    # Step 1: Fetch stock data for yesterday
    print("\n[STEP 1] Fetching stock data for yesterday...")
    yesterday = datetime.now() - timedelta(days=1)

    record = analyze_single_day(yesterday)

    if not record:
        print("ERROR: Could not fetch data. Market may not be closed yet.")
        return False

    if not record.get('companies'):
        print("ERROR: No stock data retrieved.")
        return False

    print(f"  ✓ Fetched data for {record['date_display']}")
    print(f"  ✓ Found {len(record['material_changes'])} material changes")

    # Step 2: Load existing data and add new record
    print("\n[STEP 2] Saving stock data to history...")
    historical_data = load_historical_data()

    # Check if this date already exists
    existing_dates = {r['date'] for r in historical_data['records']}
    if record['date'] in existing_dates:
        print(f"  WARNING: {record['date']} already exists in history")
        print(f"  Removing old record and replacing with new data...")
        historical_data['records'] = [r for r in historical_data['records'] if r['date'] != record['date']]

    historical_data['records'].append(record)
    save_historical_data(historical_data)
    print(f"  ✓ Saved to {historical_data}")

    # Step 3: Research news for material changes
    if record['material_changes']:
        print(f"\n[STEP 3] Researching news for {len(record['material_changes'])} material changes...")

        for i, change in enumerate(record['material_changes'], 1):
            ticker = change['ticker']
            name = change['name']
            pct_change = change['data']['pct_change']
            current_price = change['data']['current_price']
            open_price = change['data']['open_price']

            print(f"\n  [{i}/{len(record['material_changes'])}] {ticker}: {pct_change:+.2f}%")

            # Research news (placeholder for now - will add WebSearch integration)
            news = research_news_for_material_change(
                ticker,
                name,
                pct_change,
                record['date_display'],
                current_price,
                open_price
            )

            # Update the news in the record
            change['news'] = news

        # Save updated data with researched news
        save_historical_data(historical_data)
        print(f"\n  ✓ Updated news summaries in history file")
    else:
        print("\n[STEP 3] No material changes to research (all stocks < ±2%)")

    # Step 4: Regenerate dashboard
    print("\n[STEP 4] Regenerating dashboard...")
    dashboard_file = generate_html_dashboard()
    print(f"  ✓ Dashboard updated: {dashboard_file}")

    # Step 5: Summary
    print("\n" + "=" * 70)
    print("DAILY UPDATE COMPLETE")
    print("=" * 70)
    print(f"Date: {record['date_display']}")
    print(f"Material Changes: {len(record['material_changes'])}")
    if record['material_changes']:
        print("\nMaterial Changes:")
        for change in record['material_changes']:
            ticker = change['ticker']
            pct = change['data']['pct_change']
            print(f"  • {ticker}: {pct:+.2f}%")
    print("\n⚠️  NOTE: News summaries need manual research and update")
    print("    Run a separate script to populate news with real context")
    print("=" * 70)

    return True

if __name__ == "__main__":
    success = update_yesterday()
    sys.exit(0 if success else 1)

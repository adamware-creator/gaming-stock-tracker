#!/usr/bin/env python3
"""
Earnings Tracker for Gaming Stocks
Fetches quarterly financial data and management presentation summaries
"""
import yfinance as yf
from datetime import datetime
import json
import os
import pandas as pd

# Import from main script
from gaming_stock_tracker_v3 import GAMING_COMPANIES

EARNINGS_FILE = 'earnings_data.json'

# Investor relations URLs for each company
INVESTOR_RELATIONS = {
    'DKNG': 'https://investors.draftkings.com',
    'FLUT': 'https://www.flutter.com/investors',
    'CZR': 'https://investor.caesars.com',
    'MGM': 'https://investors.mgmresorts.com',
    'PENN': 'https://investors.pennentertainment.com',
    'RSI': 'https://www.rushstreetinteractive.com/investors',
    'BALY': 'https://investors.ballys.com'
}

def load_earnings_data():
    """Load existing earnings data"""
    if os.path.exists(EARNINGS_FILE):
        with open(EARNINGS_FILE, 'r') as f:
            return json.load(f)
    return {"companies": {}}

def save_earnings_data(data):
    """Save earnings data"""
    with open(EARNINGS_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_quarters_since_q1_2024():
    """Generate list of quarters from Q1 2024 to current quarter"""
    quarters = []
    start_year = 2024
    current_date = datetime.now()
    current_year = current_date.year
    current_quarter = (current_date.month - 1) // 3 + 1

    for year in range(start_year, current_year + 1):
        start_q = 1 if year > start_year else 1
        end_q = current_quarter if year == current_year else 4

        for q in range(start_q, end_q + 1):
            quarters.append(f"Q{q} {year}")

    return quarters

def fetch_quarterly_financials(ticker):
    """Fetch quarterly financial data from yfinance"""
    try:
        stock = yf.Ticker(ticker)
        quarters_data = {}

        # Get quarterly income statement (this has revenue and net income)
        try:
            quarterly_financials = stock.quarterly_financials

            if quarterly_financials is not None and not quarterly_financials.empty:
                # Transpose to get dates as index
                for date_col in quarterly_financials.columns[:8]:  # Get last 8 quarters
                    quarter_date = date_col

                    # Filter for 2024 onwards
                    if quarter_date.year < 2024:
                        continue

                    # Determine quarter
                    quarter_num = (quarter_date.month - 1) // 3 + 1
                    quarter_key = f"Q{quarter_num} {quarter_date.year}"

                    # Get revenue (Total Revenue or just Revenue)
                    revenue = None
                    for rev_key in ['Total Revenue', 'Revenue']:
                        if rev_key in quarterly_financials.index:
                            revenue = quarterly_financials.loc[rev_key, date_col]
                            break

                    # Get net income
                    net_income = None
                    for income_key in ['Net Income', 'Net Income Common Stockholders']:
                        if income_key in quarterly_financials.index:
                            net_income = quarterly_financials.loc[income_key, date_col]
                            break

                    quarters_data[quarter_key] = {
                        'date': quarter_date.strftime('%Y-%m-%d'),
                        'revenue': float(revenue) if revenue is not None and not pd.isna(revenue) else None,
                        'earnings': float(net_income) if net_income is not None and not pd.isna(net_income) else None,
                        'presentation_summary': None,
                        'ir_url': INVESTOR_RELATIONS.get(ticker, '')
                    }

                print(f"    [OK] Fetched financials from quarterly_financials")
                return quarters_data

        except Exception as e:
            print(f"    Warning: quarterly_financials failed: {e}")

        # Try alternative: quarterly income statement
        try:
            quarterly_income = stock.quarterly_income_stmt

            if quarterly_income is not None and not quarterly_income.empty:
                for date_col in quarterly_income.columns[:8]:
                    quarter_date = date_col

                    if quarter_date.year < 2024:
                        continue

                    quarter_num = (quarter_date.month - 1) // 3 + 1
                    quarter_key = f"Q{quarter_num} {quarter_date.year}"

                    # Get revenue
                    revenue = None
                    for rev_key in ['Total Revenue', 'Revenue']:
                        if rev_key in quarterly_income.index:
                            revenue = quarterly_income.loc[rev_key, date_col]
                            break

                    # Get net income
                    net_income = None
                    for income_key in ['Net Income', 'Net Income Common Stockholders']:
                        if income_key in quarterly_income.index:
                            net_income = quarterly_income.loc[income_key, date_col]
                            break

                    quarters_data[quarter_key] = {
                        'date': quarter_date.strftime('%Y-%m-%d'),
                        'revenue': float(revenue) if revenue is not None and not pd.isna(revenue) else None,
                        'earnings': float(net_income) if net_income is not None and not pd.isna(net_income) else None,
                        'presentation_summary': None,
                        'ir_url': INVESTOR_RELATIONS.get(ticker, '')
                    }

                print(f"    [OK] Fetched financials from quarterly_income_stmt")
                return quarters_data

        except Exception as e:
            print(f"    Warning: quarterly_income_stmt failed: {e}")

        # If still no data, create placeholder structure
        if not quarters_data:
            print(f"    [WARN] No financial data available, creating placeholders")
            all_quarters = get_quarters_since_q1_2024()
            for quarter in all_quarters:
                quarters_data[quarter] = {
                    'date': None,
                    'revenue': None,
                    'earnings': None,
                    'presentation_summary': None,
                    'ir_url': INVESTOR_RELATIONS.get(ticker, '')
                }

        return quarters_data

    except Exception as e:
        print(f"    Error fetching data for {ticker}: {e}")
        return {}

def calculate_yoy_changes(quarters_data):
    """Calculate year-over-year percentage changes for revenue and earnings"""
    sorted_quarters = sorted(quarters_data.items(), key=lambda x: x[0])

    for i, (quarter, data) in enumerate(sorted_quarters):
        # Find the same quarter from previous year
        quarter_num, year = quarter.split()
        prev_year_quarter = f"{quarter_num} {int(year) - 1}"

        if prev_year_quarter in quarters_data:
            prev_data = quarters_data[prev_year_quarter]

            # Calculate revenue YoY
            if data.get('revenue') and prev_data.get('revenue'):
                revenue_yoy = ((data['revenue'] - prev_data['revenue']) / prev_data['revenue']) * 100
                data['revenue_yoy'] = round(revenue_yoy, 1)
            else:
                data['revenue_yoy'] = None

            # Calculate earnings YoY
            if data.get('earnings') and prev_data.get('earnings'):
                earnings_yoy = ((data['earnings'] - prev_data['earnings']) / prev_data['earnings']) * 100
                data['earnings_yoy'] = round(earnings_yoy, 1)
            else:
                data['earnings_yoy'] = None
        else:
            data['revenue_yoy'] = None
            data['earnings_yoy'] = None

    return quarters_data

def fetch_all_earnings():
    """Fetch earnings data for all tracked companies"""
    print("Fetching earnings data for all companies...")
    print("=" * 70)

    earnings_data = load_earnings_data()

    for ticker, name in GAMING_COMPANIES.items():
        print(f"\nFetching {name} ({ticker})...")

        quarters_data = fetch_quarterly_financials(ticker)

        if ticker not in earnings_data['companies']:
            earnings_data['companies'][ticker] = {
                'name': name,
                'quarters': {}
            }

        # Update with new data
        earnings_data['companies'][ticker]['quarters'].update(quarters_data)

        # Calculate YoY changes
        earnings_data['companies'][ticker]['quarters'] = calculate_yoy_changes(
            earnings_data['companies'][ticker]['quarters']
        )

        # Save after each company
        save_earnings_data(earnings_data)

        if quarters_data:
            # Count how many have actual data vs placeholders
            with_data = sum(1 for q in quarters_data.values() if q.get('revenue') is not None or q.get('earnings') is not None)
            print(f"  [OK] Fetched {len(quarters_data)} quarters ({with_data} with financial data)")
        else:
            print(f"  [SKIP] No data available")

    print(f"\n{'=' * 70}")
    print(f"Earnings data saved to {EARNINGS_FILE}")
    return earnings_data

def update_presentation_summary(ticker, quarter, summary):
    """Update management presentation summary for a specific quarter"""
    earnings_data = load_earnings_data()

    if ticker not in earnings_data['companies']:
        print(f"ERROR: {ticker} not found in earnings data")
        return False

    if quarter not in earnings_data['companies'][ticker]['quarters']:
        print(f"ERROR: {quarter} not found for {ticker}")
        print(f"Available quarters: {', '.join(earnings_data['companies'][ticker]['quarters'].keys())}")
        return False

    earnings_data['companies'][ticker]['quarters'][quarter]['presentation_summary'] = summary
    save_earnings_data(earnings_data)

    print(f"[OK] Updated presentation summary for {ticker} {quarter}")
    return True

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 1:
        # Fetch all earnings data
        fetch_all_earnings()
    elif len(sys.argv) == 4:
        # Update specific presentation summary
        ticker = sys.argv[1]
        quarter = sys.argv[2]
        summary = sys.argv[3]
        update_presentation_summary(ticker, quarter, summary)
    else:
        print("Usage:")
        print("  python earnings_tracker.py                    # Fetch all earnings data")
        print('  python earnings_tracker.py TICKER QUARTER "Summary text"  # Update presentation summary')
        print("\nExample:")
        print('  python earnings_tracker.py DKNG "Q1 2024" "Management highlighted..."')

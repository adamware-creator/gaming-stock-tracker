#!/usr/bin/env python3
"""
Refresh all historical data with unadjusted prices
"""
import warnings
warnings.filterwarnings('ignore')

from curl_cffi import requests as curl_requests
# Patch for SSL
try:
    original_request = curl_requests.Session.request
    def patched_request(self, *args, **kwargs):
        kwargs['verify'] = False
        return original_request(self, *args, **kwargs)
    curl_requests.Session.request = patched_request
except:
    pass

import yfinance as yf
from datetime import datetime, timedelta
import json
import time
import urllib.parse

# Configuration
GAMING_COMPANIES = {
    'FLUT': 'Flutter Entertainment',
    'DKNG': 'DraftKings',
    'MGM': 'MGM Resorts',
    'CZR': 'Caesars Entertainment',
    'PENN': 'Penn Entertainment',
    'RSI': 'Rush Street Interactive',
    'BALY': "Bally's Corporation"
}

BENCHMARK = '^IXIC'
MATERIAL_CHANGE_THRESHOLD = 2.0
DATA_FILE = 'stock_tracker_history.json'

# Configure session with Edge 101 impersonation
session = curl_requests.Session(impersonate='edge101')
session.verify = False

def get_stock_data(ticker, date):
    """Fetch stock data for a specific date"""
    max_retries = 2
    for attempt in range(max_retries):
        try:
            end_date = date + timedelta(days=1)
            start_date = date - timedelta(days=5)

            hist = yf.download(
                ticker,
                start=start_date,
                end=end_date,
                auto_adjust=False,
                progress=False,
                session=session
            )

            if hist.empty:
                return None

            # Find the row for our target date
            date_str = date.strftime('%Y-%m-%d')
            if date_str not in hist.index.strftime('%Y-%m-%d').tolist():
                return None

            row = hist.loc[date_str]

            current_price = row['Close']
            open_price = row['Open']
            volume = row['Volume']
            pct_change = ((current_price - open_price) / open_price) * 100

            return {
                'current_price': float(current_price),
                'open_price': float(open_price),
                'pct_change': float(pct_change),
                'volume': int(volume)
            }
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            print(f"    Error: {e}")
            return None
    return None

def build_search_query(company_name, ticker, pct_change, date_str):
    """Build search query for news"""
    direction = "rises" if pct_change > 0 else "drops"
    return f"{company_name} {ticker} stock {direction} {date_str}"

print("=" * 70)
print("REFRESH HISTORICAL DATA WITH UNADJUSTED PRICES")
print("=" * 70)
print()

# Load existing historical data
with open(DATA_FILE, 'r') as f:
    historical_data = json.load(f)

# Get all records except December 15 (already has correct data)
records_to_refresh = [r for r in historical_data['records'] if r['date'] != '2025-12-15']
records_to_refresh = sorted(records_to_refresh, key=lambda x: x['date'])

print(f"Found {len(records_to_refresh)} records to refresh")
print(f"Estimated time: ~{len(records_to_refresh) * 10 / 60:.1f} minutes")
print()

for i, record in enumerate(records_to_refresh):
    date_obj = datetime.strptime(record['date'], '%Y-%m-%d')
    date_display = record['date_display']

    print(f"[{i+1}/{len(records_to_refresh)}] Refreshing {date_display}...")

    # Get benchmark data
    benchmark_data = get_stock_data(BENCHMARK, date_obj)
    if benchmark_data:
        print(f"  NASDAQ: ${benchmark_data['current_price']:.2f} ({benchmark_data['pct_change']:+.2f}%)")
    time.sleep(0.5)

    # Update record structure
    updated_record = {
        'date': record['date'],
        'date_display': date_display,
        'benchmark': benchmark_data,
        'companies': {},
        'material_changes': []
    }

    # Fetch data for each gaming company
    for ticker, name in GAMING_COMPANIES.items():
        data = get_stock_data(ticker, date_obj)

        if data:
            updated_record['companies'][ticker] = {
                'name': name,
                'data': data
            }

            # Check if change exceeds threshold
            if abs(data['pct_change']) >= MATERIAL_CHANGE_THRESHOLD:
                search_query = build_search_query(name, ticker, data['pct_change'], date_display)

                updated_record['material_changes'].append({
                    'ticker': ticker,
                    'name': name,
                    'data': data,
                    'search_query': search_query,
                    'news': {
                        'search_query': search_query,
                        'summary': f"{name} stock {'rises' if data['pct_change'] > 0 else 'drops'} {abs(data['pct_change']):.1f}% on {date_display}",
                        'needs_manual_lookup': True
                    }
                })

        time.sleep(0.5)  # Delay between requests

    print(f"  Completed: {len(updated_record['companies'])} companies, {len(updated_record['material_changes'])} material changes")

    # Update the record in historical_data
    for j, r in enumerate(historical_data['records']):
        if r['date'] == record['date']:
            historical_data['records'][j] = updated_record
            break

    # Save after each date (in case of interruption)
    with open(DATA_FILE, 'w') as f:
        json.dump(historical_data, f, indent=2)

    print()

print(f"[OK] All historical data refreshed with unadjusted prices!")
print(f"     Total records: {len(historical_data['records'])}")

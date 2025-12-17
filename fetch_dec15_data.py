#!/usr/bin/env python3
"""
Fetch December 15, 2025 stock data and add to historical records
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
    try:
        end_date = date + timedelta(days=1)
        start_date = date - timedelta(days=3)

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
        print(f"  Error fetching {ticker}: {e}")
        return None

def build_search_query(company_name, ticker, pct_change, date_str):
    """Build search query for news"""
    direction = "rises" if pct_change > 0 else "drops"
    return f"{company_name} {ticker} stock {direction} {date_str}"

print("=" * 70)
print("FETCH DECEMBER 15, 2025 DATA")
print("=" * 70)
print()

target_date = datetime(2025, 12, 15)
date_str = target_date.strftime('%Y-%m-%d')
date_display = target_date.strftime('%B %d, %Y')

print(f"Fetching data for {date_display}...")
print()

# Get benchmark data
print(f"Fetching {BENCHMARK}...")
benchmark_data = get_stock_data(BENCHMARK, target_date)
if benchmark_data:
    print(f"  OK - ${benchmark_data['current_price']:.2f} ({benchmark_data['pct_change']:+.2f}%)")
else:
    print(f"  Failed to fetch benchmark")
time.sleep(1)

# Track results
results = {
    'date': date_str,
    'date_display': date_display,
    'benchmark': benchmark_data,
    'companies': {},
    'material_changes': []
}

# Fetch data for each gaming company
for ticker, name in GAMING_COMPANIES.items():
    print(f"Fetching {ticker} ({name})...")
    data = get_stock_data(ticker, target_date)

    if data:
        print(f"  OK - ${data['current_price']:.2f} ({data['pct_change']:+.2f}%)")

        results['companies'][ticker] = {
            'name': name,
            'data': data
        }

        # Check if change exceeds threshold
        if abs(data['pct_change']) >= MATERIAL_CHANGE_THRESHOLD:
            search_query = build_search_query(name, ticker, data['pct_change'], date_display)

            results['material_changes'].append({
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
            print(f"  ** MATERIAL CHANGE **")
    else:
        print(f"  Failed to fetch")

    time.sleep(1)  # Delay between requests

# Load existing historical data
with open(DATA_FILE, 'r') as f:
    historical_data = json.load(f)

# Check if December 15 already exists and remove it
historical_data['records'] = [r for r in historical_data['records'] if r['date'] != date_str]

# Add new record
historical_data['records'].append(results)

# Save updated data
with open(DATA_FILE, 'w') as f:
    json.dump(historical_data, f, indent=2)

print()
print(f"[OK] Saved December 15 data to {DATA_FILE}")
print(f"     Companies: {len(results['companies'])}")
print(f"     Material changes: {len(results['material_changes'])}")

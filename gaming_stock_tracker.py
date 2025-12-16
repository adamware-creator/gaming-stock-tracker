#!/usr/bin/env python3
"""
Gaming Stock Tracker - Phase 2
Tracks major online gaming companies against NASDAQ benchmark
Flags any stock with ±2% or greater price movement
Searches for news explaining material changes
"""

import yfinance as yf
from datetime import datetime
import webbrowser
import urllib.parse

# Configuration
GAMING_COMPANIES = {
    'DKNG': 'DraftKings',
    'FLUT.L': 'Flutter Entertainment',
    'CZR': 'Caesars Entertainment',
    'MGM': 'MGM Resorts',
    'PENN': 'Penn Entertainment',
    'RSI': 'Rush Street Interactive',
    'BALY': 'Bally\'s Corporation',
    'FUBO': 'fuboTV'
}

BENCHMARK = '^IXIC'  # NASDAQ Composite Index
MATERIAL_CHANGE_THRESHOLD = 2.0  # 2% threshold

def build_search_query(company_name, ticker, pct_change, date_str):
    """
    Build a smart, time-specific search query for stock news
    Uses the strategy: company + ticker + direction + specific date
    """
    direction = "rises" if pct_change > 0 else "drops"

    # Build targeted query: "CompanyName TICKER stock drops December 12 2025"
    query = f"{company_name} {ticker} stock {direction} {date_str}"
    return query

def get_stock_data(ticker):
    """Fetch current stock data for a given ticker"""
    try:
        stock = yf.Ticker(ticker)
        # Get recent data (last 2 days to ensure we have today's open)
        hist = stock.history(period='2d')

        if hist.empty:
            return None

        current_price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[-1]

        # Calculate percentage change from today's open
        pct_change = ((current_price - open_price) / open_price) * 100

        return {
            'current_price': current_price,
            'open_price': open_price,
            'pct_change': pct_change
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def main():
    """Main function to track gaming stocks"""
    # Get today's date for search queries
    now = datetime.now()
    date_str = now.strftime('%B %d %Y')  # "December 12 2025"

    print("=" * 70)
    print("GAMING STOCK TRACKER - Phase 2")
    print(f"Report generated: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()

    # Get benchmark data
    print("Fetching benchmark data (NASDAQ)...")
    benchmark_data = get_stock_data(BENCHMARK)

    if benchmark_data:
        print(f"NASDAQ: ${benchmark_data['current_price']:.2f} ({benchmark_data['pct_change']:+.2f}%)")
    else:
        print("Warning: Could not fetch NASDAQ data")

    print()
    print("-" * 70)
    print("GAMING COMPANIES")
    print("-" * 70)
    print()

    # Track companies with material changes
    material_changes = []

    # Fetch data for each gaming company
    for ticker, name in GAMING_COMPANIES.items():
        print(f"Fetching {name} ({ticker})...", end=" ")
        data = get_stock_data(ticker)

        if data:
            pct_change = data['pct_change']
            print(f"${data['current_price']:.2f} ({pct_change:+.2f}%)")

            # Check if change exceeds threshold
            if abs(pct_change) >= MATERIAL_CHANGE_THRESHOLD:
                material_changes.append({
                    'ticker': ticker,
                    'name': name,
                    'data': data
                })
        else:
            print("FAILED")

    # Display material changes summary with news search
    print()
    print("=" * 70)
    print("MATERIAL CHANGES (±2% or more)")
    print("=" * 70)
    print()

    if material_changes:
        for i, item in enumerate(material_changes, 1):
            data = item['data']
            direction = "UP" if data['pct_change'] > 0 else "DOWN"

            print(f"{i}. {item['name']} ({item['ticker']})")
            print(f"   Open:    ${data['open_price']:.2f}")
            print(f"   Current: ${data['current_price']:.2f}")
            print(f"   Change:  {data['pct_change']:+.2f}% {direction}")
            print()

            # Build smart search query
            search_query = build_search_query(
                item['name'],
                item['ticker'],
                data['pct_change'],
                date_str
            )

            # Create Google search URL
            encoded_query = urllib.parse.quote(search_query)
            search_url = f"https://www.google.com/search?q={encoded_query}"

            print(f"   Search Query: \"{search_query}\"")
            print(f"   News Search:  {search_url}")
            print()

        # Ask if user wants to open search results in browser
        print("-" * 70)
        response = input("\nOpen news searches in browser? (y/n): ").strip().lower()
        if response == 'y':
            for item in material_changes:
                data = item['data']
                search_query = build_search_query(
                    item['name'],
                    item['ticker'],
                    data['pct_change'],
                    date_str
                )
                encoded_query = urllib.parse.quote(search_query)
                search_url = f"https://www.google.com/search?q={encoded_query}"
                webbrowser.open(search_url)
                print(f"Opened search for {item['name']}")
    else:
        print("No material changes detected. All stocks within ±2% range.")

    print()
    print("=" * 70)
    print("Report complete!")
    print("=" * 70)

if __name__ == "__main__":
    main()

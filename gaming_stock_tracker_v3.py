#!/usr/bin/env python3
"""
Gaming Stock Tracker - Phase 3
Tracks major online gaming companies against NASDAQ benchmark
Stores historical data and generates HTML dashboard
"""

import yfinance as yf
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
import warnings

# Disable SSL warnings (workaround for Windows SSL certificate issues)
warnings.filterwarnings('ignore')

# Patch curl_cffi to disable SSL verification
try:
    from curl_cffi import requests as curl_requests
    original_request = curl_requests.Session.request

    def patched_request(self, *args, **kwargs):
        kwargs['verify'] = False
        return original_request(self, *args, **kwargs)

    curl_requests.Session.request = patched_request
except ImportError:
    pass

# Configuration
GAMING_COMPANIES = {
    'DKNG': 'DraftKings',
    'FLUT': 'Flutter Entertainment',
    'CZR': 'Caesars Entertainment',
    'MGM': 'MGM Resorts',
    'PENN': 'Penn Entertainment',
    'RSI': 'Rush Street Interactive',
    'BALY': 'Bally\'s Corporation'
}

# Company logo URLs (using Clearbit Logo API)
COMPANY_LOGOS = {
    'DKNG': 'https://logo.clearbit.com/draftkings.com',
    'FLUT': 'https://logo.clearbit.com/flutter.com',
    'CZR': 'https://logo.clearbit.com/caesars.com',
    'MGM': 'https://logo.clearbit.com/mgmresorts.com',
    'PENN': 'https://logo.clearbit.com/pennentertainment.com',
    'RSI': 'https://logo.clearbit.com/rushstreetinteractive.com',
    'BALY': 'https://logo.clearbit.com/ballys.com'
}

BENCHMARK = '^IXIC'  # NASDAQ Composite Index
MATERIAL_CHANGE_THRESHOLD = 2.0  # 2% threshold
DATA_FILE = 'stock_tracker_history.json'
DASHBOARD_FILE = 'stock_dashboard.html'

def load_historical_data():
    """Load existing historical data from JSON file"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"records": []}

def save_historical_data(data):
    """Save historical data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_stock_data(ticker, date=None):
    """
    Fetch stock data for a given ticker
    If date is provided, fetch historical data for that specific day
    """
    try:
        stock = yf.Ticker(ticker)

        if date:
            # Fetch data for specific date (need a range to get that day's data)
            end_date = date + timedelta(days=1)
            start_date = date - timedelta(days=5)  # Get a few days to ensure we have the data
            hist = stock.history(start=start_date, end=end_date)
        else:
            # Get recent data (last 2 days for today)
            hist = stock.history(period='2d')

        if hist.empty:
            return None

        # Get the last available day's data
        current_price = hist['Close'].iloc[-1]
        open_price = hist['Open'].iloc[-1]
        volume = hist['Volume'].iloc[-1]

        # Calculate percentage change from open
        pct_change = ((current_price - open_price) / open_price) * 100

        return {
            'current_price': float(current_price),
            'open_price': float(open_price),
            'pct_change': float(pct_change),
            'volume': int(volume)
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return None

def get_news_summary(ticker, company_name, pct_change, date_str):
    """
    Fetch recent news for a stock ticker using web search
    NOTE: This is a placeholder that stores the search query.
    In production, you would call a web search API here.
    """
    direction = "rises" if pct_change > 0 else "drops"
    search_query = f"{company_name} {ticker} stock {direction} {date_str}"

    # Store search query for manual lookup
    # In a production system, you would make an API call here
    return {
        'search_query': search_query,
        'summary': f"{company_name} stock {direction} {abs(pct_change):.1f}% on {date_str}",
        'needs_manual_lookup': True
    }

def build_search_query(company_name, ticker, pct_change, date_str):
    """Build a smart, time-specific search query for stock news"""
    direction = "rises" if pct_change > 0 else "drops"
    query = f"{company_name} {ticker} stock {direction} {date_str}"
    return query

def analyze_single_day(target_date=None):
    """
    Analyze stocks for a single day
    If target_date is None, analyze yesterday (most recent completed trading day)
    Returns a record of the day's analysis
    """
    if target_date is None:
        # Default to yesterday to ensure market is closed and news is available
        target_date = datetime.now() - timedelta(days=1)

    # Validate that the date is not today or in the future
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    check_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)

    if check_date >= today:
        print(f"ERROR: Cannot analyze {target_date.strftime('%B %d, %Y')} - market hasn't closed yet!")
        print("Please wait until the next day to ensure accurate data and news availability.")
        return None

    date_str = target_date.strftime('%Y-%m-%d')
    date_display = target_date.strftime('%B %d, %Y')

    print(f"\nAnalyzing {date_display}...")

    # Get benchmark data
    benchmark_data = get_stock_data(BENCHMARK, target_date if target_date != datetime.now() else None)

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
        data = get_stock_data(ticker, target_date if target_date != datetime.now() else None)

        if data:
            results['companies'][ticker] = {
                'name': name,
                'data': data
            }

            # Check if change exceeds threshold
            if abs(data['pct_change']) >= MATERIAL_CHANGE_THRESHOLD:
                search_query = build_search_query(name, ticker, data['pct_change'], date_display)
                news_summary = get_news_summary(ticker, name, data['pct_change'], date_display)

                results['material_changes'].append({
                    'ticker': ticker,
                    'name': name,
                    'data': data,
                    'search_query': search_query,
                    'news': news_summary
                })

    return results

def analyze_historical(days=30):
    """Run analysis for the last N trading days"""
    print(f"=" * 70)
    print(f"HISTORICAL ANALYSIS - Last {days} Days")
    print(f"=" * 70)

    historical_data = load_historical_data()
    existing_dates = {record['date'] for record in historical_data['records']}

    # Generate list of dates to analyze
    today = datetime.now()
    dates_to_analyze = []

    for i in range(days):
        check_date = today - timedelta(days=i)
        # Skip weekends (rough filter - doesn't account for holidays)
        if check_date.weekday() < 5:  # Monday = 0, Friday = 4
            date_str = check_date.strftime('%Y-%m-%d')
            if date_str not in existing_dates:
                dates_to_analyze.append(check_date)

    # Analyze each date
    for date in reversed(dates_to_analyze):  # Oldest first
        record = analyze_single_day(date)
        if record['companies']:  # Only save if we got data
            historical_data['records'].append(record)
            save_historical_data(historical_data)
            print(f"  [OK] Saved data for {record['date_display']}")

    print(f"\nHistorical analysis complete! {len(dates_to_analyze)} days analyzed.")
    return historical_data

def load_earnings_data():
    """Load earnings data from JSON file"""
    earnings_file = 'earnings_data.json'
    if os.path.exists(earnings_file):
        with open(earnings_file, 'r') as f:
            return json.load(f)
    return {"companies": {}}

def generate_industry_summary():
    """Generate industry summary for most recent quarter across all companies"""
    earnings_data = load_earnings_data()

    # Find the most recent quarter across all companies
    most_recent_quarter = None
    for ticker, company_data in earnings_data['companies'].items():
        quarters = company_data.get('quarters', {})
        for quarter in quarters.keys():
            if quarters[quarter].get('presentation_summary'):
                if most_recent_quarter is None or quarter > most_recent_quarter:
                    most_recent_quarter = quarter

    if not most_recent_quarter:
        return ""

    # Collect summaries from all companies for this quarter
    summaries = []
    for ticker, company_data in sorted(earnings_data['companies'].items()):
        name = company_data.get('name', ticker)
        quarters = company_data.get('quarters', {})
        if most_recent_quarter in quarters:
            data = quarters[most_recent_quarter]
            if data.get('presentation_summary'):
                summaries.append({
                    'ticker': ticker,
                    'name': name,
                    'summary': data['presentation_summary']
                })

    if not summaries:
        return ""

    # Generate industry overview
    html = f"""
    <div style="background: linear-gradient(135deg, #0047FF 0%, #0056CC 100%); padding: 25px 30px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,71,255,0.2);">
        <h2 style="color: white; font-size: 1.5em; margin-bottom: 15px; font-weight: 700;">Industry Overview: {most_recent_quarter}</h2>
        <div style="color: rgba(255,255,255,0.95); font-size: 0.95em; line-height: 1.7;">
            <p style="margin-bottom: 10px;"><strong style="color: white;">Gaming Industry {most_recent_quarter} Highlights:</strong></p>
            <p>The gaming sector showed mixed performance across {len(summaries)} companies. Key themes included digital growth momentum, regional gaming challenges, strategic transformations, and evolving regulatory landscapes. Companies focused on cost optimization, market share expansion, and preparing for upcoming market opportunities while navigating customer-friendly sports outcomes and operational headwinds.</p>
        </div>
    </div>
    """

    return html

def generate_earnings_tracker_html():
    """Generate HTML for the earnings tracker tab"""
    earnings_data = load_earnings_data()

    html = ""

    # Check if we have any earnings data
    if not earnings_data.get('companies'):
        html += """
            <div style="padding: 40px; text-align: center; background: white; border-radius: 8px; margin: 20px 0;">
                <h2 style="color: #0047FF; margin-bottom: 15px;">No Earnings Data Available</h2>
                <p style="color: #555; margin-bottom: 20px;">Run <code>python earnings_tracker.py</code> to fetch earnings data.</p>
            </div>
        """
        return html

    # Add industry summary
    html += generate_industry_summary()

    # Generate earnings cards for each company
    company_index = 0
    for ticker, company_data in earnings_data['companies'].items():
        name = company_data.get('name', ticker)
        quarters = company_data.get('quarters', {})
        logo_url = COMPANY_LOGOS.get(ticker, '')

        if not quarters:
            continue

        company_index += 1

        # Organize quarters by year
        quarters_2024 = {}
        quarters_2025 = {}

        for quarter, data in quarters.items():
            if '2024' in quarter:
                quarters_2024[quarter] = data
            elif '2025' in quarter:
                quarters_2025[quarter] = data

        # Build HTML for company (collapsible)
        html += f"""
        <div class="company-card" style="background: white; padding: 0; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); overflow: hidden;">
            <div class="company-header" onclick="toggleCompany('company-{company_index}')" style="display: flex; align-items: center; gap: 12px; padding: 20px 25px; cursor: pointer; background: white; border-bottom: 2px solid #f0f0f0; transition: background 0.2s;">
                <svg class="collapse-arrow" id="arrow-{company_index}" style="width: 20px; height: 20px; fill: #0047FF; transition: transform 0.3s;" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M7.41 8.59L12 13.17l4.59-4.58L18 10l-6 6-6-6 1.41-1.41z"/>
                </svg>
                <img src="{logo_url}" alt="{name}" style="width: 32px; height: 32px; object-fit: contain; border-radius: 4px;" onerror="this.style.display='none'">
                <h2 style="color: #0047FF; font-size: 1.4em; margin: 0; flex: 1;">{name} ({ticker})</h2>
                <a href="{list(quarters.values())[0].get('ir_url', '#')}" target="_blank" onclick="event.stopPropagation();" style="padding: 6px 14px; background: #FF4500; color: white; text-decoration: none; border-radius: 20px; font-size: 0.8em; font-weight: 600;">Investor Relations →</a>
            </div>

            <div id="company-{company_index}" class="company-content" style="padding: 25px; background: #fafafa;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
        """

        # Helper function to generate quarter card
        def generate_quarter_card(quarter, data):
            if data is None:
                # Placeholder for missing quarter
                return f"""
                    <div style="background: #f0f0f0; padding: 15px; border-radius: 6px; border-left: 4px solid #ccc; opacity: 0.5;">
                        <div style="font-weight: 700; color: #999; font-size: 1em; margin-bottom: 10px;">{quarter}</div>
                        <div style="color: #999; font-size: 0.85em; font-style: italic;">No data available</div>
                    </div>
                """

            revenue = data.get('revenue')
            earnings = data.get('earnings')
            revenue_yoy = data.get('revenue_yoy')
            earnings_yoy = data.get('earnings_yoy')
            presentation_summary = data.get('presentation_summary')

            # Format financial numbers
            revenue_str = f"${revenue/1e9:.2f}B" if revenue else "N/A"
            earnings_str = f"${earnings/1e9:.2f}B" if earnings else "N/A"

            # Format YoY changes with color
            revenue_yoy_str = ""
            if revenue_yoy is not None:
                yoy_color = "#28a745" if revenue_yoy > 0 else "#dc3545"
                revenue_yoy_str = f'<span style="color: {yoy_color}; font-size: 0.85em; font-weight: 600;">({revenue_yoy:+.1f}% YoY)</span>'

            earnings_yoy_str = ""
            if earnings_yoy is not None:
                yoy_color = "#28a745" if earnings_yoy > 0 else "#dc3545"
                earnings_yoy_str = f'<span style="color: {yoy_color}; font-size: 0.85em; font-weight: 600;">({earnings_yoy:+.1f}% YoY)</span>'

            card_html = f"""
                <div style="background: #f8f9fa; padding: 15px; border-radius: 6px; border-left: 4px solid #0047FF;">
                    <div style="font-weight: 700; color: #0047FF; font-size: 1em; margin-bottom: 10px;">{quarter}</div>

                    <div style="display: flex; gap: 20px; margin-bottom: 12px;">
                        <div>
                            <div style="color: #666; font-size: 0.75em; font-weight: 600; text-transform: uppercase;">Revenue</div>
                            <div style="color: #1a1a1a; font-weight: 700; font-size: 1em;">{revenue_str} {revenue_yoy_str}</div>
                        </div>
                        <div>
                            <div style="color: #666; font-size: 0.75em; font-weight: 600; text-transform: uppercase;">Earnings</div>
                            <div style="color: #1a1a1a; font-weight: 700; font-size: 1em;">{earnings_str} {earnings_yoy_str}</div>
                        </div>
                    </div>
            """

            if presentation_summary:
                card_html += f"""
                    <div style="background: white; padding: 12px; border-radius: 4px; border-left: 3px solid #FF4500; margin-top: 10px;">
                        <div style="font-weight: 700; color: #0047FF; font-size: 0.75em; text-transform: uppercase; margin-bottom: 6px;">Management Presentation</div>
                        <div style="color: #333; font-size: 0.88em; line-height: 1.5;">{presentation_summary}</div>
                    </div>
                """

            card_html += """
                </div>
            """

            return card_html

        # Column 1: 2024
        html += '<div style="display: flex; flex-direction: column; gap: 15px;">'
        html += '<div style="background: #0047FF; color: white; padding: 10px 15px; border-radius: 6px; font-weight: 700; text-align: center; font-size: 1.1em;">2024</div>'
        for q in ['Q1 2024', 'Q2 2024', 'Q3 2024', 'Q4 2024']:
            html += generate_quarter_card(q, quarters_2024.get(q))
        html += '</div>'

        # Column 2: 2025
        html += '<div style="display: flex; flex-direction: column; gap: 15px;">'
        html += '<div style="background: #FF4500; color: white; padding: 10px 15px; border-radius: 6px; font-weight: 700; text-align: center; font-size: 1.1em;">2025</div>'
        for q in ['Q1 2025', 'Q2 2025', 'Q3 2025', 'Q4 2025']:
            html += generate_quarter_card(q, quarters_2025.get(q))
        html += '</div>'

        html += """
                </div>
            </div>
        </div>
        """

    return html

def generate_html_dashboard():
    """Generate an HTML dashboard from historical data"""
    historical_data = load_historical_data()

    if not historical_data['records']:
        print("No historical data found. Run analysis first.")
        return

    # Sort records by date (newest first)
    records = sorted(historical_data['records'], key=lambda x: x['date'], reverse=True)

    # Get date range
    oldest_date = records[-1]['date_display'] if records else 'N/A'
    newest_date = records[0]['date_display'] if records else 'N/A'

    # Create company list
    company_list = '<br>'.join([f"• {name} ({ticker})" for ticker, name in GAMING_COMPANIES.items()])

    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gaming Stock Tracker Dashboard</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0047FF;
            padding: 0;
            min-height: 100vh;
        }}

        .top-banner {{
            background: #FF4500;
            color: white;
            padding: 8px 20px;
            font-size: 0.85em;
            font-weight: 500;
            position: sticky;
            top: 0;
            z-index: 100;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .banner-logo {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 700;
            font-size: 1em;
        }}

        .banner-logo-icon {{
            width: 18px;
            height: 18px;
            fill: white;
        }}

        .banner-center {{
            flex: 1;
            text-align: center;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px 15px;
        }}

        .header {{
            background: white;
            padding: 20px 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 15px;
            display: grid;
            grid-template-columns: 2fr 1fr 1fr;
            gap: 25px;
            align-items: start;
        }}

        .header-main {{
            border-right: 2px solid #f0f0f0;
            padding-right: 25px;
        }}

        h1 {{
            color: #0047FF;
            font-size: 1.8em;
            margin-bottom: 6px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }}

        .subtitle {{
            color: #333;
            font-size: 0.9em;
            font-weight: 400;
        }}

        .header-section {{
            padding-left: 10px;
        }}

        .header-section-title {{
            color: #0047FF;
            font-size: 0.75em;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}

        .header-section-content {{
            color: #555;
            font-size: 0.85em;
            line-height: 1.6;
        }}

        .date-range {{
            color: #777;
            font-size: 0.8em;
            margin-top: 4px;
        }}


        .day-card {{
            background: white;
            padding: 20px 25px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 12px;
        }}

        .day-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 12px;
            border-bottom: 2px solid #f0f0f0;
            position: sticky;
            top: 35px;
            background: white;
            z-index: 10;
            margin-left: -25px;
            margin-right: -25px;
            margin-top: -20px;
            padding: 15px 25px 12px 25px;
            border-radius: 8px 8px 0 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}

        .day-title {{
            font-size: 1.3em;
            color: #0047FF;
            font-weight: 700;
        }}

        .benchmark {{
            font-size: 0.9em;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            background: #f5f5f5;
        }}

        .benchmark.positive {{
            background: #d4edda;
            color: #155724;
        }}

        .benchmark.negative {{
            background: #f8d7da;
            color: #721c24;
        }}

        .material-changes {{
            margin-top: 12px;
        }}

        .change-item {{
            background: #f8f9fa;
            padding: 15px 18px;
            border-left: 4px solid #0047FF;
            margin-bottom: 12px;
            border-radius: 6px;
            transition: all 0.2s ease;
        }}

        .change-item:hover {{
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transform: translateY(-1px);
        }}

        .change-item.positive {{
            border-left-color: #28a745;
            background: #f0fdf4;
        }}

        .change-item.negative {{
            border-left-color: #dc3545;
            background: #fef2f2;
        }}

        .company-name {{
            font-size: 1.05em;
            font-weight: 700;
            margin-bottom: 6px;
            color: #1a1a1a;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .company-logo {{
            width: 24px;
            height: 24px;
            object-fit: contain;
            border-radius: 4px;
        }}

        .data-row {{
            display: flex;
            align-items: center;
            gap: 20px;
            flex-wrap: wrap;
        }}

        .price-info {{
            display: flex;
            gap: 20px;
            align-items: center;
        }}

        .price-item {{
            display: flex;
            gap: 6px;
            align-items: baseline;
        }}

        .price-label {{
            color: #666;
            font-size: 0.75em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .price-value {{
            font-weight: 700;
            font-size: 0.95em;
            color: #1a1a1a;
        }}

        .search-link {{
            display: inline-block;
            margin-top: 8px;
            padding: 6px 14px;
            background: #FF4500;
            color: white;
            text-decoration: none;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            transition: all 0.2s ease;
        }}

        .search-link:hover {{
            background: #e03e00;
            transform: translateY(-1px);
            box-shadow: 0 2px 6px rgba(255,69,0,0.3);
        }}

        .no-changes {{
            color: #666;
            font-style: italic;
            padding: 15px;
            text-align: center;
            background: #f8f9fa;
            border-radius: 6px;
            font-size: 0.9em;
        }}

        .news-inline {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex: 1;
            min-width: 0;
        }}

        .news-text {{
            color: #333;
            font-size: 0.88em;
            line-height: 1.4;
            flex: 1;
            min-width: 0;
        }}

        .news-button {{
            display: inline-block;
            padding: 5px 12px;
            background: #1a1a2e;
            color: white;
            text-decoration: none;
            border-radius: 20px;
            font-size: 0.75em;
            font-weight: 600;
            transition: all 0.2s ease;
            white-space: nowrap;
            flex-shrink: 0;
        }}

        .news-button:hover {{
            background: #0047FF;
            box-shadow: 0 2px 6px rgba(0,71,255,0.3);
        }}

        .separator {{
            color: #ccc;
            margin: 0 4px;
        }}

        .tabs {{
            display: flex;
            gap: 0;
            margin-bottom: 15px;
            background: white;
            border-radius: 8px;
            padding: 5px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            position: sticky;
            top: 35px;
            z-index: 50;
        }}

        .tab {{
            flex: 1;
            padding: 12px 20px;
            background: transparent;
            border: none;
            color: #555;
            font-weight: 600;
            font-size: 0.95em;
            cursor: pointer;
            border-radius: 6px;
            transition: all 0.2s ease;
        }}

        .tab:hover {{
            background: #f5f5f5;
            color: #0047FF;
        }}

        .tab.active {{
            background: #0047FF;
            color: white;
        }}

        .tab-content {{
            display: none;
        }}

        .tab-content.active {{
            display: block;
        }}

        .company-header:hover {{
            background: #f8f9fa !important;
        }}

        .company-content {{
            max-height: 5000px;
            opacity: 1;
            transition: max-height 0.4s ease, opacity 0.3s ease;
        }}

        .company-content.collapsed {{
            max-height: 0;
            opacity: 0;
            padding: 0 25px !important;
            overflow: hidden;
        }}
    </style>
</head>
<body>
    <div class="top-banner">
        <div class="banner-logo">
            <svg class="banner-logo-icon" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M12 2L4 5v6.09c0 5.05 3.41 9.76 8 10.91 4.59-1.15 8-5.86 8-10.91V5l-8-3z"/>
            </svg>
            <span>GeoComply</span>
        </div>
        <div class="banner-center">Gaming Stock Intelligence • Real-time tracking of material market movements</div>
        <div style="width: 120px;"></div>
    </div>
    <div class="container">
        <div class="header">
            <div class="header-main">
                <h1>Gaming Stock Tracker Dashboard</h1>
                <p class="subtitle">Monitoring {len(GAMING_COMPANIES)} gaming companies for material changes (±{MATERIAL_CHANGE_THRESHOLD}%)</p>
            </div>
            <div class="header-section">
                <div class="header-section-title">Trading Days</div>
                <div class="header-section-content">
                    <strong>{len(records)}</strong> days tracked
                    <div class="date-range">{oldest_date} to {newest_date}</div>
                </div>
            </div>
            <div class="header-section">
                <div class="header-section-title">Companies Monitored</div>
                <div class="header-section-content">{company_list}</div>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="switchTab('material-changes')">Material Changes</button>
            <button class="tab" onclick="switchTab('earnings-tracker')">Earnings Tracker</button>
        </div>

        <div id="material-changes" class="tab-content active">
"""

    # Add each day's record
    for record in records:
        benchmark = record.get('benchmark', {})
        bench_change = benchmark.get('pct_change', 0) if benchmark else 0
        bench_class = 'positive' if bench_change > 0 else 'negative'

        html += f"""
        <div class="day-card">
            <div class="day-header">
                <div class="day-title">{record['date_display']}</div>
"""

        if benchmark:
            html += f"""
                <div class="benchmark {bench_class}">
                    NASDAQ: ${benchmark['current_price']:.2f} ({bench_change:+.2f}%)
                </div>
"""

        html += """
            </div>
"""

        if record['material_changes']:
            html += """
            <div class="material-changes">
"""
            for change in record['material_changes']:
                data = change['data']
                direction_class = 'positive' if data['pct_change'] > 0 else 'negative'
                direction = 'UP' if data['pct_change'] > 0 else 'DOWN'

                # Add news summary and search link
                import urllib.parse
                news = change.get('news', {})
                search_query = news.get('search_query') or change.get('search_query', '')
                summary = news.get('summary', '')
                search_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"

                ticker = change['ticker']
                logo_url = COMPANY_LOGOS.get(ticker, '')

                html += f"""
                <div class="change-item {direction_class}">
                    <div class="company-name">
                        <img src="{logo_url}" alt="{change['name']}" class="company-logo" onerror="this.style.display='none'">
                        <span>{change['name']} ({ticker})</span>
                    </div>
                    <div class="data-row">
                        <div class="price-info">
                            <div class="price-item">
                                <span class="price-label">Open:</span>
                                <span class="price-value">${data['open_price']:.2f}</span>
                            </div>
                            <div class="price-item">
                                <span class="price-label">Close:</span>
                                <span class="price-value">${data['current_price']:.2f}</span>
                            </div>
                            <div class="price-item">
                                <span class="price-label">Change:</span>
                                <span class="price-value">{data['pct_change']:+.2f}% {direction}</span>
                            </div>
                        </div>
"""

                if summary:
                    html += f"""
                        <span class="separator">•</span>
                        <div class="news-inline">
                            <div class="news-text">{summary}</div>
                            <a href="{search_url}" target="_blank" class="news-button">Find News →</a>
                        </div>
"""
                else:
                    html += f"""
                        <a href="{search_url}" target="_blank" class="search-link">Search News →</a>
"""

                html += """
                    </div>
                </div>
"""

            html += """
            </div>
"""
        else:
            html += """
            <div class="no-changes">No material changes detected on this day</div>
"""

        html += """
        </div>
"""

    html += """
        </div>

        <div id="earnings-tracker" class="tab-content">
    """

    # Add earnings tracker content
    html += generate_earnings_tracker_html()

    html += """
        </div>
    </div>

    <script>
        function switchTab(tabId) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});

            // Show selected tab
            document.getElementById(tabId).classList.add('active');
            event.target.classList.add('active');
        }}

        function toggleCompany(companyId) {{
            const content = document.getElementById(companyId);
            const arrowId = companyId.replace('company-', 'arrow-');
            const arrow = document.getElementById(arrowId);

            if (content.classList.contains('collapsed')) {{
                content.classList.remove('collapsed');
                arrow.style.transform = 'rotate(0deg)';
            }} else {{
                content.classList.add('collapsed');
                arrow.style.transform = 'rotate(-90deg)';
            }}
        }}
    </script>
</body>
</html>
"""

    # Write HTML file
    with open(DASHBOARD_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n[OK] Dashboard generated: {DASHBOARD_FILE}")
    return DASHBOARD_FILE

def main():
    """Main function"""
    import sys

    print("=" * 70)
    print("GAMING STOCK TRACKER - Phase 3")
    print("Historical Analysis & Dashboard")
    print("=" * 70)
    print()
    print("Options:")
    print("1. Analyze yesterday (most recent completed trading day)")
    print("2. Run 30-day historical analysis")
    print("3. Generate dashboard from existing data")
    print()

    choice = input("Select option (1-3): ").strip()

    if choice == '1':
        # Analyze yesterday (most recent completed trading day)
        record = analyze_single_day()
        if record is None:
            return

        historical_data = load_historical_data()

        # Check if this date already exists and update, or add new
        existing_index = None
        for i, r in enumerate(historical_data['records']):
            if r['date'] == record['date']:
                existing_index = i
                break

        if existing_index is not None:
            historical_data['records'][existing_index] = record
            print("Updated record")
        else:
            historical_data['records'].append(record)
            print("Added new record")

        save_historical_data(historical_data)
        generate_html_dashboard()

    elif choice == '2':
        # Run historical analysis
        analyze_historical(30)
        generate_html_dashboard()

    elif choice == '3':
        # Just generate dashboard
        generate_html_dashboard()

    else:
        print("Invalid choice")

if __name__ == "__main__":
    main()

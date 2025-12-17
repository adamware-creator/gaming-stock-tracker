#!/usr/bin/env python3
"""
Automated Daily Stock Tracker Update
Runs via GitHub Actions at 6am ET on weekdays
Uses Vertex AI Claude + Google Custom Search for full automation
"""

import os
import sys
import json
import requests
import base64
from datetime import datetime, timedelta
from google.cloud import aiplatform
from google.oauth2 import service_account
import anthropic

# Add project directory to path
sys.path.insert(0, '.')
from gaming_stock_tracker_v3 import (
    analyze_single_day,
    load_historical_data,
    save_historical_data,
    generate_html_dashboard,
    GAMING_COMPANIES
)

# Configuration
GCP_PROJECT_ID = None  # Will be extracted from service account
GCP_LOCATION = "us-east5"  # Vertex AI location
CLAUDE_MODEL = "claude-3-5-sonnet-v2@20241022"

def setup_gcp_credentials():
    """Setup GCP credentials from GitHub secret"""
    global GCP_PROJECT_ID

    creds_json = os.environ.get('GCP_SERVICE_ACCOUNT_KEY')
    if not creds_json:
        print("ERROR: GCP_SERVICE_ACCOUNT_KEY not found in environment")
        sys.exit(1)

    # Parse credentials
    creds_dict = json.loads(creds_json)
    GCP_PROJECT_ID = creds_dict['project_id']

    # Write credentials to temporary file
    creds_path = '/tmp/gcp_credentials.json'
    with open(creds_path, 'w') as f:
        f.write(creds_json)

    # Set environment variable for GCP SDK
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds_path

    print(f"✓ GCP credentials configured (Project: {GCP_PROJECT_ID})")
    return creds_dict

def search_web(query):
    """Search the web using Google Custom Search API"""
    api_key = os.environ.get('GOOGLE_SEARCH_API_KEY')
    search_engine_id = os.environ.get('GOOGLE_SEARCH_ENGINE_ID')

    if not api_key or not search_engine_id:
        print("ERROR: Google Search API credentials not found")
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        'key': api_key,
        'cx': search_engine_id,
        'q': query,
        'num': 5  # Get top 5 results
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        results = []
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'snippet': item.get('snippet', ''),
                'link': item.get('link', '')
            })

        return results

    except Exception as e:
        print(f"WARNING: Search failed for '{query}': {e}")
        return []

def call_claude_vertex(prompt, search_results=None):
    """Call Claude via Vertex AI to generate news narrative"""

    # Initialize Vertex AI
    aiplatform.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)

    # Build the prompt with search results if available
    full_prompt = prompt
    if search_results:
        full_prompt += "\n\nWeb search results:\n"
        for i, result in enumerate(search_results, 1):
            full_prompt += f"\n{i}. {result['title']}\n"
            full_prompt += f"   {result['snippet']}\n"
            full_prompt += f"   URL: {result['link']}\n"

    # Call Claude via Vertex AI
    endpoint = f"projects/{GCP_PROJECT_ID}/locations/{GCP_LOCATION}/publishers/anthropic/models/{CLAUDE_MODEL}"

    # Create client
    from google.cloud.aiplatform_v1.services.prediction_service import PredictionServiceClient
    client = PredictionServiceClient(
        client_options={"api_endpoint": f"{GCP_LOCATION}-aiplatform.googleapis.com"}
    )

    # Prepare request
    instance = {
        "anthropic_version": "vertex-2023-10-16",
        "messages": [
            {
                "role": "user",
                "content": full_prompt
            }
        ],
        "max_tokens": 1024,
        "temperature": 1.0
    }

    # Make request
    response = client.predict(
        endpoint=endpoint,
        instances=[instance]
    )

    # Extract response
    if response.predictions:
        prediction = response.predictions[0]
        if 'content' in prediction and len(prediction['content']) > 0:
            return prediction['content'][0]['text']

    return None

def research_material_change(ticker, name, pct_change, date_display, current_price):
    """Research and generate news narrative for a material change"""

    print(f"\n  Researching {ticker} ({pct_change:+.2f}%)...")

    # Step 1: Search the web
    direction = "up" if pct_change > 0 else "down"
    search_query = f"{name} {ticker} stock {direction} {date_display}"

    print(f"    Searching: {search_query}")
    search_results = search_web(search_query)

    if not search_results:
        print(f"    WARNING: No search results found")
    else:
        print(f"    Found {len(search_results)} search results")

    # Step 2: Ask Claude to write narrative
    direction_verb = "rose" if pct_change > 0 else "fell"

    prompt = f"""Based on the web search results provided, write a concise 2-3 sentence news narrative explaining why {name} ({ticker}) stock {direction_verb} {abs(pct_change):.1f}% on {date_display} to close at ${current_price:.2f}.

Requirements:
- Use past tense and {direction_verb} (not rises/drops)
- Include specific catalysts: analyst actions, earnings news, competitive developments, regulatory changes, or market events
- Mention stock performance context (YTD, vs 52-week high, etc.) if relevant
- Keep it factual and concise
- Write in third person

Write only the narrative, no introduction or explanation."""

    print(f"    Calling Claude via Vertex AI...")
    narrative = call_claude_vertex(prompt, search_results)

    if narrative:
        print(f"    ✓ Generated narrative ({len(narrative)} chars)")
        return {
            'search_query': search_query,
            'summary': narrative.strip(),
            'needs_manual_lookup': False
        }
    else:
        print(f"    WARNING: Claude returned no narrative")
        # Fallback to placeholder
        return {
            'search_query': search_query,
            'summary': f"{name} {direction_verb} {abs(pct_change):.1f}% on {date_display}.",
            'needs_manual_lookup': True
        }

def main():
    """Main automation workflow"""
    print("=" * 70)
    print("AUTOMATED DAILY UPDATE - Gaming Stock Tracker")
    print("=" * 70)
    print()

    # Setup
    print("[1/6] Setting up GCP credentials...")
    setup_gcp_credentials()
    print()

    # Fetch stock data
    print("[2/6] Fetching stock data for yesterday...")
    yesterday = datetime.now() - timedelta(days=1)

    record = analyze_single_day(yesterday)

    if not record or not record.get('companies'):
        print("INFO: No stock data available for yesterday")
        print("This is normal for market holidays (Thanksgiving, Christmas, etc.)")
        print("Exiting gracefully - no update needed")
        sys.exit(0)  # Exit successfully, not an error

    print(f"✓ Fetched data for {record['date_display']}")
    print(f"  Companies: {len(record['companies'])}")
    print(f"  Material changes: {len(record['material_changes'])}")
    print()

    # Research news for material changes
    if record['material_changes']:
        print(f"[3/6] Researching news for {len(record['material_changes'])} material changes...")

        for i, change in enumerate(record['material_changes'], 1):
            ticker = change['ticker']
            name = change['name']
            pct_change = change['data']['pct_change']
            current_price = change['data']['current_price']

            print(f"\n  [{i}/{len(record['material_changes'])}] {ticker}: {pct_change:+.2f}% → ${current_price:.2f}")

            # Research and update news
            news = research_material_change(
                ticker,
                name,
                pct_change,
                record['date_display'],
                current_price
            )

            change['news'] = news
    else:
        print("[3/6] No material changes to research")
    print()

    # Save to history
    print("[4/6] Saving to stock_tracker_history.json...")
    historical_data = load_historical_data()

    # Remove if already exists
    existing_dates = {r['date'] for r in historical_data['records']}
    if record['date'] in existing_dates:
        print(f"  Removing existing record for {record['date']}")
        historical_data['records'] = [r for r in historical_data['records'] if r['date'] != record['date']]

    historical_data['records'].append(record)
    save_historical_data(historical_data)
    print("✓ Data saved")
    print()

    # Regenerate dashboard
    print("[5/6] Regenerating dashboard...")
    dashboard_file = generate_html_dashboard()
    print(f"✓ Dashboard updated: {dashboard_file}")
    print()

    # Send to Slack
    print("[6/6] Sending to Slack...")
    slack_webhook = os.environ.get('SLACK_WEBHOOK_URL')

    if slack_webhook:
        # Import and use slack notifier
        from slack_notifier import format_slack_message, send_to_slack

        message = format_slack_message(record)
        success = send_to_slack(message)

        if success:
            print("✓ Slack notification sent")
        else:
            print("WARNING: Slack notification failed")
    else:
        print("WARNING: SLACK_WEBHOOK_URL not set, skipping Slack notification")

    print()
    print("=" * 70)
    print("✓ AUTOMATED UPDATE COMPLETE")
    print("=" * 70)
    print(f"Date: {record['date_display']}")
    print(f"Material Changes: {len(record['material_changes'])}")

    if record['material_changes']:
        print("\nMaterial Changes:")
        for change in record['material_changes']:
            ticker = change['ticker']
            pct = change['data']['pct_change']
            print(f"  • {ticker}: {pct:+.2f}%")

    print()

if __name__ == "__main__":
    main()

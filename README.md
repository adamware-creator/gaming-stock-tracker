# Gaming Stock Tracker

A comprehensive stock tracking and analysis dashboard for the online gaming industry.

## Overview

This project monitors 7 major gaming companies for material price changes (±2% threshold) and provides:
- Daily stock price tracking against NASDAQ benchmark
- Historical analysis and visualization
- Quarterly earnings tracking and summaries
- Interactive HTML dashboard with material changes and earnings data

## Companies Tracked

- **DKNG** - DraftKings
- **FLUT** - Flutter Entertainment
- **CZR** - Caesars Entertainment
- **MGM** - MGM Resorts
- **PENN** - Penn Entertainment
- **RSI** - Rush Street Interactive
- **BALY** - Bally's Corporation

## Features

### Stock Tracker (`gaming_stock_tracker_v3.py`)
- Tracks daily price movements vs NASDAQ Composite (^IXIC)
- Identifies material changes (±2%)
- Generates Google News search queries for significant movements
- Stores historical data in JSON format

### Dashboard (`index.html`)
- **Material Changes Tab**: Daily tracking with price data and news links
- **Earnings Tracker Tab**: Quarterly earnings with management presentation summaries
- Modern, responsive UI with company logos
- Sticky headers and collapsible sections

### Earnings Tracker (`earnings_tracker.py`)
- Fetches quarterly earnings data
- Stores revenue, earnings, and YoY growth
- Management presentation summaries

### Slack Integration (`slack_notifier.py`)
- Daily automated Slack notifications
- Material changes alerts (±2%)
- All companies performance summary
- Link to live dashboard
- See [SLACK_SETUP.md](SLACK_SETUP.md) for configuration instructions

## Installation

```bash
pip install yfinance pandas requests
```

For Slack notifications, see [SLACK_SETUP.md](SLACK_SETUP.md) for additional configuration.

## Usage

### Run Stock Analysis

```bash
python gaming_stock_tracker_v3.py
```

Options:
1. Analyze yesterday (most recent completed trading day)
2. Run 30-day historical analysis
3. Generate dashboard from existing data

### View Dashboard

Open `index.html` in your web browser after running the tracker, or visit the live dashboard at https://adamware-creator.github.io/gaming-stock-tracker/

### Send Slack Update

After configuring Slack (see [SLACK_SETUP.md](SLACK_SETUP.md)):

```bash
python send_slack_update.py
```

This sends the latest stock data to your configured Slack channel.

## Data Files

- `stock_tracker_history.json` - Historical stock price data and material changes
- `earnings_data.json` - Quarterly earnings data and summaries
- `index.html` - Generated dashboard (updated on each run)

## Requirements

- Python 3.7+
- yfinance
- pandas

## Notes

- The tracker analyzes completed trading days (excludes weekends and current day)
- Material change threshold is set to ±2%
- Dashboard automatically updates when tracker runs
- SSL certificate bypass implemented for Windows environments

## License

Private project for internal use.

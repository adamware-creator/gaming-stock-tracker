#!/usr/bin/env python3
"""
Update December 15 news summaries with actual context
"""
import json

# Load data
with open('stock_tracker_history.json', 'r') as f:
    data = json.load(f)

# Find December 15 record
for record in data['records']:
    if record['date'] == '2025-12-15':
        # Update PENN news
        for change in record['material_changes']:
            if change['ticker'] == 'PENN':
                change['news']['summary'] = 'PENN Entertainment closed down -3.70% on December 15 amid continued pressure following its December 1 termination of the ESPN Bet partnership and Q3 2025 earnings miss (-$0.22 vs -$0.05 expected). Stock trading below $14 as company pivots focus to theScore Bet brand.'
                change['news']['needs_manual_lookup'] = False

            elif change['ticker'] == 'RSI':
                change['news']['summary'] = 'Rush Street Interactive dropped -2.27% intraday on December 15 (opened $19.39, closed $18.95) despite positive analyst coverage. Susquehanna raised price target to $23 (from $22) maintaining Positive rating, citing favorable Colombia tax developments and strong Latin America performance. Broader market weakness (NASDAQ -1.17%) likely contributed to intraday decline.'
                change['news']['needs_manual_lookup'] = False

        break

# Save updated data
with open('stock_tracker_history.json', 'w') as f:
    json.dump(data, f, indent=2)

print('[OK] Updated December 15 news summaries')
print()
print('PENN: ESPN Bet termination aftermath, Q3 earnings pressure')
print('RSI: Intraday drop despite analyst upgrade and Colombia tax news')

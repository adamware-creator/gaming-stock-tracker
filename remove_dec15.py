#!/usr/bin/env python3
"""Remove December 15th from history since market hasn't closed"""
import json

# Load data
with open('stock_tracker_history.json', 'r') as f:
    data = json.load(f)

# Remove Dec 15th
original_count = len(data['records'])
data['records'] = [r for r in data['records'] if r['date'] != '2025-12-15']
new_count = len(data['records'])

# Save
with open('stock_tracker_history.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f'Removed {original_count - new_count} record(s) for December 15th')
print(f'Total records now: {new_count}')

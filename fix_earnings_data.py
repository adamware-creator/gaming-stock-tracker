#!/usr/bin/env python3
"""
Fix earnings data:
1. Replace /usr/bin/bash with $
2. Calculate missing YoY percentages
"""

import json
import sys
import io

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Load earnings data
with open('earnings_data.json', 'r') as f:
    data = json.load(f)

# Fix /usr/bin/bash errors and calculate YoY
for ticker, company_data in data['companies'].items():
    quarters = company_data.get('quarters', {})

    # Fix /usr/bin/bash errors in summaries
    for quarter, quarter_data in quarters.items():
        if quarter_data.get('presentation_summary'):
            summary = quarter_data['presentation_summary']
            # Replace /usr/bin/bash with $
            summary = summary.replace('/usr/bin/bash', '$')
            quarter_data['presentation_summary'] = summary

    # Calculate missing YoY percentages
    for quarter, quarter_data in quarters.items():
        # Skip if already has YoY data
        if quarter_data.get('revenue_yoy') is not None and quarter_data.get('earnings_yoy') is not None:
            continue

        # Parse quarter (e.g., "Q1 2025")
        parts = quarter.split()
        if len(parts) != 2:
            continue

        q_num = parts[0]  # "Q1", "Q2", etc.
        year = int(parts[1])  # 2025, 2024, etc.

        # Find the same quarter from previous year
        prev_year_quarter = f"{q_num} {year - 1}"

        if prev_year_quarter in quarters:
            prev_data = quarters[prev_year_quarter]

            # Calculate revenue YoY
            if quarter_data.get('revenue') and prev_data.get('revenue'):
                current_revenue = quarter_data['revenue']
                prev_revenue = prev_data['revenue']
                if prev_revenue > 0:
                    revenue_yoy = ((current_revenue - prev_revenue) / prev_revenue) * 100
                    quarter_data['revenue_yoy'] = round(revenue_yoy, 1)

            # Calculate earnings YoY
            if quarter_data.get('earnings') is not None and prev_data.get('earnings') is not None:
                current_earnings = quarter_data['earnings']
                prev_earnings = prev_data['earnings']
                # Handle earnings YoY carefully (can go from negative to positive, etc.)
                if prev_earnings != 0:
                    earnings_yoy = ((current_earnings - prev_earnings) / abs(prev_earnings)) * 100
                    quarter_data['earnings_yoy'] = round(earnings_yoy, 1)

# Save fixed data
with open('earnings_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print("✅ Fixed earnings data:")
print("  - Replaced /usr/bin/bash with $")
print("  - Calculated missing YoY percentages")

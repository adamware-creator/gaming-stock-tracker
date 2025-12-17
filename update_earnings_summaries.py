#!/usr/bin/env python3
"""
Update earnings summaries with comprehensive Q&A and market reaction
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

# Updated comprehensive summaries with Q&A and market reaction

updates = {
    ('DKNG', 'Q3 2024'): "DraftKings Q3 2024: Revenue $1.10B (+39% YoY), EBITDA loss $59M. Online sportsbook GGR +39%, iGaming +26%, new customer acquisition +14% with CAC down 20% YoY. NFL parlay mix increased 500bps driven by product improvements and marketing. Analysts questioned Illinois tax strategy and prediction markets potential; CEO Robins highlighted opportunities in non-sports betting markets ahead of next presidential election. Revised FY2024 guidance to $4.85-4.95B revenue (from $5.05-5.25B) due to customer-friendly Q4 sports outcomes. Introduced FY2025 guidance of $6.2-6.6B revenue (+31% YoY). Stock declined 6% in extended trading on wider-than-expected loss and lowered guidance, despite maintaining Strong Buy consensus with $49.08 average price target (+26% upside).",

    ('DKNG', 'Q4 2024'): "DraftKings Q4 2024: Revenue $1.39B (in line with estimates), EPS $0.14 (beat $0.11 expected). Full year 2024 revenue $4.8B (+30% YoY), achieved positive free cash flow for first time while acquiring 3.5M new customers at record low CAC. Total customer base 10.1M (+42% YoY). Analysts questioned promotional intensity and handle growth slowdown; CEO Robins expects 'quite a decline in promotional intensity' in 2025 and attributed Q4 slowdown to one less NFL game and election distractions, with rapid acceleration post-election. Discussed prediction markets interest pending CFTC decisions. Raised FY2025 revenue guidance low end to $6.3-6.6B (from $6.2-6.6B). Stock traded higher on bottom-line beat and raised guidance, targeting 30% EBITDA margins over time.",

    ('FLUT', 'Q3 2024'): "Flutter Q3 2024: Revenue $3.25B (+27% YoY, beating estimates by 7%), EBITDA $650M (+75% YoY, exceeding estimates by 25%). FanDuel revenue $2.2B (+51% YoY), EBITDA $358M (vs $55M loss Q3 2023), holds 41% sportsbook GGR market share and 25% iGaming market share with 3.2M average monthly players (+28% YoY). Analysts questioned promotional expenses (up 540bps vs 400bps long-term guidance) and same-game parlay impact; CEO Jackson emphasized pricing accuracy driving differentiation, confirmed SGP drives significant hold improvement. Analysts probed Brazil regulatory timeline (Jan 1 launch preparation) and FanDuel market positioning. Preparing Missouri launch Q4, Alberta Q1 2026. Stock hit new 52-week high of $265.52, rising 7% post-earnings on strong FanDuel momentum and structural margin expansion.",

    ('FLUT', 'Q4 2024'): "Flutter Q4 2024: Revenue $3.79B (+14% YoY), net income $56M, EBITDA $655M (+4% YoY). FanDuel FY2024 revenue $9.8B, EBITDA $1.07B with #1 market position (43% sportsbook GGR share, 26% iGaming). Adverse NFL outcomes impacted Q4 revenue by ~$550M and EBITDA by ~$360M. Full year 2024 revenue $14B (vs $11.7B in 2023), EBITDA $2.3B (+26% YoY). Analysts questioned $90M investment losses in Missouri/Alberta expansion and customer acquisition environment; CEO Jackson noted larger-than-anticipated business end-state particularly in iGaming, with parlay offerings and structural hold improvements exceeding guidance. Brazil targeting $100M losses for year per CFO Coldrake. Announced FY2025 FanDuel guidance of $11.4-11.9B revenue, $1.3-1.5B EBITDA. Cost efficiency programs targeting $500M+ annualized savings by 2027. Stock reaction muted due to customer-friendly sports outcomes headwind."
}

# Apply updates
for (ticker, quarter), summary in updates.items():
    if ticker in data['companies']:
        if quarter in data['companies'][ticker]['quarters']:
            data['companies'][ticker]['quarters'][quarter]['presentation_summary'] = summary
            print(f'✅ Updated: {ticker} {quarter}')
        else:
            print(f'⚠️  Quarter not found: {ticker} {quarter}')
    else:
        print(f'⚠️  Company not found: {ticker}')

# Save updated data
with open('earnings_data.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f'\n✅ Updated {len(updates)} earnings summaries with Q&A and market reaction')

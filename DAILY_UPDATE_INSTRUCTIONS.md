# Daily Update Instructions

## How to Update for Yesterday's Results

Simply say to Claude:

```
Update for yesterday's results
```

or

```
Update for 12/16
```

## What Claude Will Do Automatically

When you request a daily update, Claude will:

1. **Fetch Stock Data** - Run the tracker to get unadjusted stock prices for yesterday
2. **Identify Material Changes** - Find all stocks with ±2% or greater moves
3. **Research News** - Use WebSearch to find actual catalysts for each material change
4. **Write Narratives** - Create accurate news summaries with:
   - Correct direction (rose/fell)
   - Exact percentage change
   - Specific catalysts (analyst actions, earnings, market events)
   - Market context and sector trends
5. **Update JSON** - Save all data to stock_tracker_history.json
6. **Regenerate Dashboard** - Update index.html with new data
7. **Commit & Push** - Save to GitHub

## Result

You'll get a fully completed update with:
- ✅ Accurate unadjusted stock prices
- ✅ Researched news narratives with real context
- ✅ Correct percentages and directions
- ✅ Updated live dashboard

No manual research or follow-up needed.

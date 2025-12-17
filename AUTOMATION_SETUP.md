# Automated Daily Updates - Setup Complete ✓

## What Happens Automatically

Every **Tuesday-Saturday at 6:00 AM Eastern Time** (the day after trading days), GitHub Actions will:

1. ✅ **Fetch stock data** for the previous trading day (unadjusted prices)
2. ✅ **Identify material changes** (stocks moving ±2% or more)
3. ✅ **Search the web** for news about each material change (Google Custom Search API)
4. ✅ **Call Claude via Vertex AI** to analyze search results and write quality narratives
5. ✅ **Update files:**
   - `stock_tracker_history.json` - Add new day's data with researched news
   - `index.html` - Regenerate dashboard
6. ✅ **Commit and push** changes to GitHub
7. ✅ **Send to Slack** - Post complete update with news narratives

## Configuration

### GitHub Secrets (Already Set Up ✓)
- `GCP_SERVICE_ACCOUNT_KEY` - Google Cloud service account credentials
- `SLACK_WEBHOOK_URL` - Slack webhook for notifications
- `GOOGLE_SEARCH_API_KEY` - Google Custom Search API key
- `GOOGLE_SEARCH_ENGINE_ID` - Custom search engine ID

### Schedule
- **Runs:** Tuesday-Saturday at 6:00 AM ET (11:00 AM UTC)
- **Processes:** Previous day's trading results (Mon-Fri markets)
- **Skips:** Sundays and Mondays automatically
- **Handles:** Market holidays gracefully (exits successfully if no trading data available)

## Testing the Automation

### Option 1: Manual Trigger via GitHub
1. Go to: https://github.com/adamware-creator/gaming-stock-tracker/actions
2. Click on "Daily Stock Update" workflow
3. Click "Run workflow" button
4. Select branch: `main`
5. Click "Run workflow"

This will run the automation immediately for testing.

### Option 2: Run Locally
```bash
cd ~/Documents/gaming-stock-tracker

# Set environment variables (use your actual values)
export GCP_SERVICE_ACCOUNT_KEY='<paste JSON here>'
export SLACK_WEBHOOK_URL='<your webhook URL>'
export GOOGLE_SEARCH_API_KEY='<your API key>'
export GOOGLE_SEARCH_ENGINE_ID='<your search engine ID>'

# Run automation
python automated_daily_update.py
```

## Monitoring

### View Automation Logs
- https://github.com/adamware-creator/gaming-stock-tracker/actions

Each run will show:
- Stock data fetched
- Material changes identified
- News research progress
- Slack notification status

### Troubleshooting

**If automation fails:**
1. Check GitHub Actions logs for error messages
2. Verify all 4 secrets are set correctly
3. Ensure Google Custom Search API has not hit daily limit (100 free searches/day)
4. Check Vertex AI quota in Google Cloud Console

**If news quality is poor:**
- Google Custom Search may have limited relevant results
- Consider upgrading to Serper API for better news coverage

**If Slack notification fails:**
- Verify webhook URL is still valid
- Check Slack workspace permissions

## Cost Estimate

**Current Setup (Free Tier):**
- GitHub Actions: Free for public repos
- Google Custom Search: 100 free searches/day (typically 3-10 per day for material changes)
- Vertex AI Claude: Pay-as-you-go (~$0.10-0.50 per day for typical usage)

**Expected monthly cost: $3-15**

## First Automated Run

**Tomorrow morning at 6:00 AM ET**, the system will run for the first time automatically!

You'll receive a Slack notification with complete results including:
- Stock prices and percentage changes
- NASDAQ benchmark
- Researched news narratives for all material changes
- Link to updated dashboard

No action needed on your part - it's fully automatic!

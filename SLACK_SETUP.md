# Slack Integration Setup Guide

This guide will help you set up daily Slack notifications for the Gaming Stock Tracker.

## What You'll Get

Every morning at 8:00 AM ET, you'll receive a Slack message with:
- 📊 NASDAQ benchmark performance
- 🚨 Material changes (±2% movements)
- 📈 All 7 companies' daily performance (sorted best to worst)
- 🔗 Link to the live dashboard

## Step 1: Create Slack Channel

1. Open your Slack workspace
2. Create a new channel (e.g., `#gaming-stock-alerts`)
3. Invite team members who should see the updates

## Step 2: Create Incoming Webhook

1. Go to https://api.slack.com/apps
2. Click **"Create New App"** → **"From scratch"**
3. Name it **"Gaming Stock Tracker"**
4. Select your Slack workspace
5. Click **"Create App"**

6. In the left sidebar, click **"Incoming Webhooks"**
7. Toggle **"Activate Incoming Webhooks"** to **ON**
8. Scroll down and click **"Add New Webhook to Workspace"**
9. Select your channel (e.g., `#gaming-stock-alerts`)
10. Click **"Allow"**

11. **Copy the Webhook URL** (it looks like):
    ```
    https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX
    ```

## Step 3: Configure the Integration

1. In the project directory, copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in a text editor and paste your webhook URL:
   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/ACTUAL/WEBHOOK/URL
   ```

3. Save the file

**IMPORTANT:** The `.env` file is already in `.gitignore` and will NOT be committed to GitHub (keeps your webhook URL private).

## Step 4: Test the Integration

Run a test to make sure it works:

```bash
python send_slack_update.py
```

You should see:
- ✅ Message sent to Slack successfully!
- A message appears in your Slack channel

## Step 5: Set Up Daily Automation

### Option A: Windows Task Scheduler

1. Open **Task Scheduler**
2. Click **"Create Basic Task"**
3. Name: "Gaming Stock Slack Update"
4. Trigger: **Daily** at **8:00 AM**
5. Action: **Start a program**
   - Program: `python`
   - Arguments: `send_slack_update.py`
   - Start in: `C:\Users\YourName\Documents\gaming-stock-tracker`
6. Before the task runs, it should fetch new data first!

### Option B: Manual Updates

Simply run this command whenever you want to send an update:
```bash
python send_slack_update.py
```

## Troubleshooting

### "SLACK_WEBHOOK_URL not found"
- Make sure you created the `.env` file (not `.env.example`)
- Check that the webhook URL is on a line that says `SLACK_WEBHOOK_URL=...`
- No spaces around the `=` sign

### "Failed to send message. Status code: 404"
- Your webhook URL might be incorrect
- Go back to https://api.slack.com/apps and copy the webhook URL again

### "No data found in stock_tracker_history.json"
- Run the stock tracker first: `python gaming_stock_tracker_v3.py`
- Select option 1 to analyze yesterday's data

## Customization

### Change the Message Format

Edit `slack_notifier.py` and modify the `format_slack_message()` function.

### Change the Dashboard URL

Edit the `DASHBOARD_URL` variable in `slack_notifier.py`.

### Send to Multiple Channels

Create multiple webhooks (one per channel) and run the script multiple times with different `SLACK_WEBHOOK_URL` values.

## Example Message

Here's what the Slack message will look like:

```
📊 Gaming Stock Update - December 15, 2025
━━━━━━━━━━━━━━━━━━━━━━━━━━
🟢 NASDAQ: +1.25%
━━━━━━━━━━━━━━━━━━━━━━━━━━

🚨 Material Changes (±2%): 2

🟢 DKNG (DraftKings): +3.45% | $42.50
🔴 MGM (MGM Resorts): -2.10% | $38.20

━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 All Companies:

🟢 DKNG: +3.45% | $42.50
🟢 FLUT: +1.20% | $215.80
🟢 PENN: +0.85% | $18.95
⚪ CZR: +0.15% | $45.30
🔴 RSI: -0.50% | $12.40
🔴 BALY: -1.25% | $15.60
🔴 MGM: -2.10% | $38.20

📊 View Full Dashboard
```

## Support

If you run into issues, check:
1. `.env` file exists with correct webhook URL
2. Python `requests` library is installed: `pip install requests`
3. Stock tracker has recent data: check `stock_tracker_history.json`

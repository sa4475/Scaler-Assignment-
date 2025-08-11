#!/bin/bash
# Usage: bash trigger_reminders.sh

RENDER_URL="https://<MY_RENDER_APP_URL>/send_reminders"

response=$(curl -s $RENDER_URL)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Reminder trigger response: $response"

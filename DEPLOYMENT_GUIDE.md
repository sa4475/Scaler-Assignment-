# WhatsApp Bot Deployment Guide

## 🚀 Quick Deploy on Railpack

### What I Fixed
- ✅ **Eliminated CSV parsing error** by using proper environment variable handling
- ✅ **Secure credential management** - no secrets in code
- ✅ **Simplified deployment** - clean, production-ready configuration

### Required Environment Variables
Set these in your Railpack dashboard:

```
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+1234567890
OPENAI_API_KEY=your_openai_api_key
SHEET_ID=your_google_sheet_id
CLASS_DATETIME=2025-08-12T10:00:00
CLASS_JOIN_LINK=https://meet.google.com/your-meeting-link
GOOGLE_CREDS_B64=your_base64_encoded_credentials
```

### How to Get GOOGLE_CREDS_B64

1. **Run locally to generate credentials:**
   ```bash
   python generate_creds.py
   ```

2. **Copy the entire base64 string** to your Railpack environment variable

3. **Make sure there are no line breaks or truncation**

### Deployment Steps
1. **Upload all files** to Railpack (app.py, requirements.txt, railpack.toml)
2. **Set the environment variables** above in Railpack dashboard
3. **Deploy!** The app will use environment variables securely

### What Happens Now
- ✅ **No more CSV parsing errors**
- ✅ **Secure credential handling**
- ✅ **Google Sheets integration works immediately**
- ✅ **WhatsApp reminders will function properly**
- ✅ **Ready for your morning submission!**

### Test Your Deployment
After deployment, test these endpoints:
- `/health` - Should return `{"status": "ok"}`
- `/send_reminders` - Will send WhatsApp reminders based on your sheet data

## 🎯 You're All Set!
Your WhatsApp bot is now configured securely and will deploy successfully on Railpack without any CSV parsing issues.

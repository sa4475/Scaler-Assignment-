from flask import Flask, jsonify
from twilio.rest import Client
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openai
import os
from datetime import datetime

app = Flask(__name__)

# Environment variables
TWILIO_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = os.environ.get("TWILIO_WHATSAPP_FROM")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SHEET_ID = os.environ.get("SHEET_ID")
CLASS_DATETIME = os.environ.get("CLASS_DATETIME")  # Example: "2025-08-15T19:00:00+05:30"
CLASS_JOIN_LINK = os.environ.get("CLASS_JOIN_LINK")

# Set OpenAI key
openai.api_key = OPENAI_API_KEY

# Setup Twilio
client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)

# Setup Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
gc = gspread.authorize(creds)
sheet = gc.open_by_key(SHEET_ID).sheet1

def generate_message(name, role, when):
    prompt = f"""
    Create a short WhatsApp reminder for {name}, a {role}, for the 'Roadmap to Data Engineering' class.
    This is the {when} reminder. Keep it friendly and engaging.
    Include this join link: {CLASS_JOIN_LINK}
    """
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )
    return response["choices"][0]["message"]["content"].strip()

@app.route("/send_reminders", methods=["GET"])
def send_reminders():
    rows = sheet.get_all_values()[1:]  # skip header
    sent_count = 0

    now = datetime.now()
    class_time = datetime.fromisoformat(CLASS_DATETIME)

    for row in rows:
        if len(row) < 4:
            continue
        name, email, phone, role = row[0], row[1], row[2], row[3]
        phone_number = f"whatsapp:+91{phone.strip()}" if not phone.startswith("+") else f"whatsapp:{phone.strip()}"

        minutes_to_class = (class_time - now).total_seconds() / 60

        if 23.5*60 <= minutes_to_class <= 24.5*60:
            msg = generate_message(name, role, "24-hour")
            client.messages.create(body=msg, from_=TWILIO_WHATSAPP_FROM, to=phone_number)
            sent_count += 1
        elif 29 <= minutes_to_class <= 31:
            msg = generate_message(name, role, "30-minute")
            client.messages.create(body=msg, from_=TWILIO_WHATSAPP_FROM, to=phone_number)
            sent_count += 1

    return jsonify({"sent": sent_count})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

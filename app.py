from flask import Flask, jsonify
from twilio.rest import Client
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openai
import os
import json
from datetime import datetime

app = Flask(__name__)

# Lazy-initialized globals
_twilio_client = None
_gsheet = None


def _missing_env_vars():
    required_vars = [
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_WHATSAPP_FROM",
        "OPENAI_API_KEY",
        "SHEET_ID",
        "CLASS_DATETIME",
        "CLASS_JOIN_LINK",
        "GOOGLE_SERVICE_ACCOUNT_JSON",
    ]
    missing = [v for v in required_vars if not os.environ.get(v)]
    return missing


def _get_twilio_client() -> Client:
    global _twilio_client
    if _twilio_client is None:
        account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
        auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
        _twilio_client = Client(account_sid, auth_token)
    return _twilio_client


def _get_google_sheet():
    global _gsheet
    if _gsheet is None:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        service_account_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
        service_account_info = json.loads(service_account_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            service_account_info, scope
        )
        gc = gspread.authorize(creds)
        sheet_id = os.environ.get("SHEET_ID")
        _gsheet = gc.open_by_key(sheet_id).sheet1
    return _gsheet


def _get_class_time() -> datetime:
    class_dt = os.environ.get("CLASS_DATETIME")
    return datetime.fromisoformat(class_dt)


def generate_message(name: str, role: str, when: str) -> str:
    join_link = os.environ.get("CLASS_JOIN_LINK", "")
    prompt = f"""
    Create a short WhatsApp reminder for {name}, a {role}, for the 'Roadmap to Data Engineering' class.
    This is the {when} reminder. Keep it friendly and engaging.
    Include this join link: {join_link}
    """

    openai.api_key = os.environ.get("OPENAI_API_KEY")
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80,
    )
    return response["choices"][0]["message"]["content"].strip()


@app.route("/send_reminders", methods=["GET"])
def send_reminders():
    missing = _missing_env_vars()
    if missing:
        return (
            jsonify({
                "sent": 0,
                "error": "Missing required environment variables",
                "missing": missing,
            }),
            500,
        )

    try:
        sheet = _get_google_sheet()
        twilio_from = os.environ.get("TWILIO_WHATSAPP_FROM")
        now = datetime.now()
        class_time = _get_class_time()
    except Exception as e:
        return jsonify({"sent": 0, "error": str(e)}), 500

    try:
        rows = sheet.get_all_values()[1:]  # skip header
    except Exception as e:
        return jsonify({"sent": 0, "error": f"Sheets read failed: {e}"}), 500

    sent_count = 0
    client = _get_twilio_client()

    for row in rows:
        if len(row) < 4:
            continue
        name, _email, phone, role = row[0], row[1], row[2], row[3]
        phone_clean = phone.strip()
        phone_number = (
            f"whatsapp:+91{phone_clean}" if not phone_clean.startswith("+") else f"whatsapp:{phone_clean}"
        )

        minutes_to_class = (class_time - now).total_seconds() / 60

        try:
            if 23.5 * 60 <= minutes_to_class <= 24.5 * 60:
                msg = generate_message(name, role, "24-hour")
                client.messages.create(body=msg, from_=twilio_from, to=phone_number)
                sent_count += 1
            elif 29 <= minutes_to_class <= 31:
                msg = generate_message(name, role, "30-minute")
                client.messages.create(body=msg, from_=twilio_from, to=phone_number)
                sent_count += 1
        except Exception as e:
            # Skip this recipient on failure
            continue

    return jsonify({"sent": sent_count})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

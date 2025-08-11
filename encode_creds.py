import base64
import json

# Read the service account JSON file
with open('service_account.json', 'r') as f:
    json_content = f.read()

# Encode as base64
encoded = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')

print("GOOGLE_CREDS_B64 value:")
print(encoded)

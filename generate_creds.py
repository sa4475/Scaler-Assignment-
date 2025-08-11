#!/usr/bin/env python3
"""
Generate base64 credentials for Google Service Account
Run this locally to get the GOOGLE_CREDS_B64 value
"""

import base64
import json

def generate_base64_creds():
    try:
        # Read the service account JSON file
        with open('service_account.json', 'r') as f:
            json_content = f.read()
        
        # Encode as base64
        encoded = base64.b64encode(json_content.encode('utf-8')).decode('utf-8')
        
        print("=" * 60)
        print("GOOGLE_CREDS_B64 value:")
        print("=" * 60)
        print(encoded)
        print("=" * 60)
        print("Copy this value to your Railpack environment variable")
        print("Make sure to copy the ENTIRE string without truncation")
        print("=" * 60)
        
        return encoded
        
    except FileNotFoundError:
        print("❌ Error: service_account.json not found!")
        print("Make sure you have the service account file in the current directory")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    generate_base64_creds()

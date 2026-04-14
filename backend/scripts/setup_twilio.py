"""
scripts/setup_twilio.py — Twilio Validation & Webhook Configurator
====================================================================
Run this once after you have Twilio credentials to:
  1. Validate your Account SID + Auth Token
  2. List your phone numbers
  3. Show Vapi import instructions

Usage:
    cd backend
    python -m scripts.setup_twilio

Requirements in .env:
    TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    TWILIO_PHONE_NUMBER=+1xxxxxxxxxx
    VAPI_API_KEY=your_vapi_key
"""
import os
import sys
import httpx
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

TWILIO_SID      = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_TOKEN    = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_PHONE    = os.getenv("TWILIO_PHONE_NUMBER", "")
VAPI_KEY        = os.getenv("VAPI_API_KEY", "")
BACKEND_URL     = os.getenv("BACKEND_URL", "http://localhost:8000")


def check_keys():
    missing = []
    if not TWILIO_SID:   missing.append("TWILIO_ACCOUNT_SID")
    if not TWILIO_TOKEN: missing.append("TWILIO_AUTH_TOKEN")

    if missing:
        print("\n❌  Missing Twilio credentials in backend/.env:")
        for m in missing:
            print(f"    - {m}")
        print("""
  How to get them:
    1. Go to https://www.twilio.com/try-twilio → Create free account
    2. Verify your email + phone number
    3. From the Console Dashboard, copy:
         Account SID:  starts with AC...
         Auth Token:   click "Show" to reveal
    4. Get a free trial phone number:
         Console → Phone Numbers → Get Trial Number
    5. Paste into backend/.env
    6. Re-run this script
""")
        sys.exit(1)


def validate_credentials() -> dict:
    """Call Twilio API to verify credentials."""
    print("  Validating Twilio credentials...")
    try:
        with httpx.Client(auth=(TWILIO_SID, TWILIO_TOKEN), timeout=15) as client:
            resp = client.get(
                f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}.json"
            )
            if resp.status_code == 200:
                data = resp.json()
                print(f"  ✅  Account: {data.get('friendly_name', TWILIO_SID)}")
                print(f"       Status: {data.get('status', 'unknown')}")
                print(f"       Type:   {data.get('type', 'trial')}")
                return data
            elif resp.status_code == 401:
                print("  ❌  Invalid credentials — check Account SID and Auth Token")
                sys.exit(1)
            else:
                print(f"  ❌  Twilio returned {resp.status_code}: {resp.text}")
                sys.exit(1)
    except Exception as e:
        print(f"  ❌  Connection error: {e}")
        sys.exit(1)


def list_phone_numbers() -> list:
    """Fetch all phone numbers on the account."""
    print("\n  Fetching phone numbers...")
    try:
        with httpx.Client(auth=(TWILIO_SID, TWILIO_TOKEN), timeout=15) as client:
            resp = client.get(
                f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_SID}/IncomingPhoneNumbers.json"
            )
            if resp.status_code == 200:
                numbers = resp.json().get("incoming_phone_numbers", [])
                if numbers:
                    print(f"  Found {len(numbers)} number(s):")
                    for n in numbers:
                        caps = []
                        if n.get("capabilities", {}).get("voice"):   caps.append("Voice")
                        if n.get("capabilities", {}).get("sms"):     caps.append("SMS")
                        if n.get("capabilities", {}).get("mms"):     caps.append("MMS")
                        print(f"    📞  {n['phone_number']}  [{', '.join(caps)}]  — {n.get('friendly_name','')}")
                else:
                    print("  ⚠️   No phone numbers found on this account")
                    print("       Get one: Console → Phone Numbers → Buy a number")
                return numbers
            return []
    except Exception as e:
        print(f"  Warning: could not list numbers — {e}")
        return []


def print_vapi_import_instructions(numbers: list):
    """Print step-by-step instructions to import Twilio into Vapi."""
    phone = TWILIO_PHONE or (numbers[0]["phone_number"] if numbers else "+1XXXXXXXXXX")

    print(f"""
  ── Import Twilio Number into Vapi ─────────────────────
  
  Your Twilio credentials are valid. Now connect to Vapi:
  
  1. Go to https://vapi.ai → Phone Numbers → Click "Import"
  2. Select "Twilio" as provider
  3. Enter:
       Account SID:  {TWILIO_SID}
       Auth Token:   {TWILIO_TOKEN[:8]}{'*' * (len(TWILIO_TOKEN) - 8) if len(TWILIO_TOKEN) > 8 else '****'}
  4. Your number {phone} should appear
  5. Click on the number → Assign "SwasthAI Voice Agent"
  
  ── Or use Vapi API directly ───────────────────────────""")

    if VAPI_KEY:
        print(f"""
  Run this to import via API:
  
  curl -X POST https://api.vapi.ai/phone-number \\
    -H "Authorization: Bearer {VAPI_KEY}" \\
    -H "Content-Type: application/json" \\
    -d '{{
      "provider": "twilio",
      "number": "{phone}",
      "twilioAccountSid": "{TWILIO_SID}",
      "twilioAuthToken": "{TWILIO_TOKEN}"
    }}'
""")
    else:
        print("\n  (Set VAPI_API_KEY in .env to see the API import command)\n")

    print(f"""  ── Update your .env ───────────────────────────────────
  TWILIO_PHONE_NUMBER={phone}
  ────────────────────────────────────────────────────────
""")


def main():
    print("\n" + "═" * 60)
    print("  SwasthAI — Twilio Setup & Validation")
    print("═" * 60 + "\n")

    check_keys()

    print(f"  Account SID: {TWILIO_SID}")
    print(f"  Auth Token:  {TWILIO_TOKEN[:8]}{'*' * (len(TWILIO_TOKEN) - 8) if len(TWILIO_TOKEN) > 8 else '****'}")
    print()

    validate_credentials()
    numbers = list_phone_numbers()
    print_vapi_import_instructions(numbers)

    print("  ── WhatsApp Note ──────────────────────────────────────")
    print("  Twilio is used for VOICE CALLS via Vapi.")
    print("  For WhatsApp → use Meta WhatsApp Cloud API (free).")
    print("  See docs/API_SETUP_GUIDE.md → Section 1 for WhatsApp setup.")
    print("  ────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()

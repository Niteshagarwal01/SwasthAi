"""
scripts/setup_vapi.py — Vapi Assistant Auto-Configurator
=========================================================
Run this once after you have a VAPI_API_KEY to automatically:
  1. Create (or update) the SwasthAI voice assistant
  2. Print the assistant ID to paste into your .env

Usage:
    cd backend
    python -m scripts.setup_vapi

Requirements in .env:
    VAPI_API_KEY=your_key_here
    BACKEND_URL=https://your-backend-url.com   (or ngrok URL)
"""
import os
import sys
import json
import httpx
from pathlib import Path

# Add parent dir so we can load .env
sys.path.insert(0, str(Path(__file__).parent.parent))
from dotenv import load_dotenv
load_dotenv()

VAPI_API_KEY   = os.getenv("VAPI_API_KEY", "")
BACKEND_URL    = os.getenv("BACKEND_URL", "http://localhost:8000")


ASSISTANT_CONFIG = {
    "name": "SwasthAI Voice Agent",
    "model": {
        "provider": "custom-llm",
        "url": f"{BACKEND_URL}/webhook/vapi",
        "model": "swasthai-groq",        # label only — Vapi sends requests to your URL
        "temperature": 0.3,
        "maxTokens": 500,
        "systemPrompt": (
            "You are SwasthAI, a friendly health assistant for rural India. "
            "Listen carefully to the caller's symptoms. "
            "Ask one short follow-up question if needed. "
            "After 2-3 exchanges, give a brief health assessment in simple language. "
            "Always end critical cases with: Please call 108 immediately. "
            "Support both Hindi and English — respond in the same language the caller uses."
        ),
    },
    "voice": {
        "provider": "azure",
        "voiceId": "hi-IN-SwaraNeural",   # Hindi female voice — warm & clear
    },
    "transcriber": {
        "provider": "deepgram",
        "model": "nova-2",
        "language": "multi",              # Auto-detects Hindi/English
    },
    "firstMessage": (
        "Namaste! Main SwasthAI hoon. Aap mujhe apni takleef bataiye, main aapki madad karunga. "
        "Hello! I'm SwasthAI. Please describe your symptoms and I'll help you."
    ),
    "endCallPhrases": ["dhanyavaad", "thank you", "bye", "shukriya", "alvida"],
    "maxDurationSeconds": 300,
    "backgroundSound": "off",
    "recordingEnabled": True,
    "endCallFunctionEnabled": True,
    "serverMessages": [
        "end-of-call-report",
        "conversation-update",
    ],
    "serverUrl": f"{BACKEND_URL}/webhook/vapi",
}


def check_key():
    if not VAPI_API_KEY:
        print("\n❌  VAPI_API_KEY is not set in your .env file!")
        print("    1. Go to https://vapi.ai → Dashboard → API Keys")
        print("    2. Copy your API key")
        print(f"    3. Add it to backend/.env:  VAPI_API_KEY=your_key_here")
        print("    4. Re-run this script\n")
        sys.exit(1)


def get_existing_assistant(client: httpx.Client) -> str | None:
    """Return ID of existing SwasthAI assistant, or None."""
    resp = client.get("https://api.vapi.ai/assistant")
    if resp.status_code != 200:
        return None
    for a in resp.json():
        if a.get("name") == "SwasthAI Voice Agent":
            return a["id"]
    return None


def create_or_update_assistant(client: httpx.Client) -> dict:
    existing_id = get_existing_assistant(client)

    if existing_id:
        print(f"  Found existing assistant: {existing_id} — updating...")
        resp = client.patch(
            f"https://api.vapi.ai/assistant/{existing_id}",
            json=ASSISTANT_CONFIG,
        )
    else:
        print("  Creating new SwasthAI assistant...")
        resp = client.post(
            "https://api.vapi.ai/assistant",
            json=ASSISTANT_CONFIG,
        )

    resp.raise_for_status()
    return resp.json()


def update_env_file(assistant_id: str):
    """Write VAPI_ASSISTANT_ID back into .env."""
    env_path = Path(__file__).parent.parent / ".env"
    content = env_path.read_text()

    if "VAPI_ASSISTANT_ID=" in content:
        lines = []
        for line in content.splitlines():
            if line.startswith("VAPI_ASSISTANT_ID="):
                lines.append(f"VAPI_ASSISTANT_ID={assistant_id}")
            else:
                lines.append(line)
        env_path.write_text("\n".join(lines) + "\n")
    else:
        with open(env_path, "a") as f:
            f.write(f"\nVAPI_ASSISTANT_ID={assistant_id}\n")

    print(f"  ✅  VAPI_ASSISTANT_ID written to .env automatically")


def main():
    print("\n" + "═" * 60)
    print("  SwasthAI — Vapi Assistant Setup")
    print("═" * 60)

    check_key()

    headers = {
        "Authorization": f"Bearer {VAPI_API_KEY}",
        "Content-Type": "application/json",
    }

    with httpx.Client(headers=headers, timeout=30) as client:
        print(f"\n  Backend URL:  {BACKEND_URL}")
        print(f"  Vapi webhook: {BACKEND_URL}/webhook/vapi")
        print()

        try:
            assistant = create_or_update_assistant(client)
        except httpx.HTTPStatusError as e:
            print(f"\n❌  Vapi API error: {e.response.status_code}")
            print(f"    {e.response.text}")
            sys.exit(1)

        assistant_id = assistant["id"]
        print(f"\n  ✅  Assistant ready!")
        print(f"  ┌─────────────────────────────────────────────────────┐")
        print(f"  │  ID:   {assistant_id}")
        print(f"  │  Name: {assistant['name']}")
        print(f"  │  Voice: Azure hi-IN-SwaraNeural (Hindi)")
        print(f"  └─────────────────────────────────────────────────────┘")

        update_env_file(assistant_id)

        print(f"""
  ── Next Steps ──────────────────────────────────────────
  1. ✅  Assistant created in Vapi dashboard
  2. 🔧  Now import your Twilio number into Vapi:
         - Go to https://vapi.ai → Phone Numbers → Import
         - Select "Twilio" → paste Account SID + Auth Token
         - Assign this assistant to the number
  3. 🔧  Run setup_twilio.py to validate Twilio creds
  ────────────────────────────────────────────────────────
""")


if __name__ == "__main__":
    main()

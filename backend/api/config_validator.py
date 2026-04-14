"""
api/config_validator.py — Integration Health Check & Configuration Validator
=============================================================================
Validates all API keys on startup and provides a /api/config/status endpoint
to show which integrations are live vs mock.
"""
import os
import httpx
from fastapi import APIRouter
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/config", tags=["Configuration"])


def _check_env(key: str) -> bool:
    """Check if an env var is set and non-empty."""
    val = os.getenv(key, "")
    return bool(val and val.strip() and not val.startswith("←"))


async def _validate_groq() -> dict:
    """Validate Groq API key by listing models."""
    key = os.getenv("GROQ_API_KEY", "")
    if not key:
        return {"status": "missing", "message": "GROQ_API_KEY not set"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.groq.com/openai/v1/models",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                return {"status": "live", "message": "Groq API key valid", "model": "llama-3.3-70b-versatile"}
            else:
                return {"status": "invalid", "message": f"Groq returned {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def _validate_whatsapp() -> dict:
    """Validate WhatsApp Cloud API token."""
    token = os.getenv("WHATSAPP_TOKEN", "")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    if not token:
        return {"status": "missing", "message": "WHATSAPP_TOKEN not set → messages will be mocked"}
    if not phone_id:
        return {"status": "missing", "message": "WHATSAPP_PHONE_NUMBER_ID not set"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://graph.facebook.com/v19.0/{phone_id}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if resp.status_code == 200:
                return {"status": "live", "message": "WhatsApp token valid", "phone_number_id": phone_id}
            else:
                return {"status": "invalid", "message": f"Meta API returned {resp.status_code} — token may be expired (expires every 24h)"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def _validate_twilio() -> dict:
    """Validate Twilio credentials."""
    sid = os.getenv("TWILIO_ACCOUNT_SID", "")
    token = os.getenv("TWILIO_AUTH_TOKEN", "")
    phone = os.getenv("TWILIO_PHONE_NUMBER", "")
    if not sid:
        return {"status": "missing", "message": "TWILIO_ACCOUNT_SID not set"}
    if not token:
        return {"status": "missing", "message": "TWILIO_AUTH_TOKEN not set"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                f"https://api.twilio.com/2010-04-01/Accounts/{sid}.json",
                auth=(sid, token),
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                return {
                    "status": "live",
                    "message": f"Twilio account active: {data.get('friendly_name', 'OK')}",
                    "phone_number": phone or "not set",
                    "account_status": data.get("status", "unknown"),
                }
            else:
                return {"status": "invalid", "message": f"Twilio returned {resp.status_code} — check SID/token"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


async def _validate_vapi() -> dict:
    """Validate Vapi API key."""
    key = os.getenv("VAPI_API_KEY", "")
    assistant_id = os.getenv("VAPI_ASSISTANT_ID", "")
    if not key:
        return {"status": "missing", "message": "VAPI_API_KEY not set → voice calls will not work"}
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(
                "https://api.vapi.ai/assistant",
                headers={"Authorization": f"Bearer {key}"},
                timeout=10,
            )
            if resp.status_code == 200:
                assistants = resp.json()
                return {
                    "status": "live",
                    "message": f"Vapi key valid — {len(assistants)} assistant(s) found",
                    "assistant_id": assistant_id or "not set",
                    "assistants_count": len(assistants),
                }
            else:
                return {"status": "invalid", "message": f"Vapi returned {resp.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def _validate_database() -> dict:
    """Check database configuration."""
    url = os.getenv("DATABASE_URL", "")
    if not url:
        return {"status": "missing", "message": "DATABASE_URL not set — using SQLite fallback"}
    if "neon" in url.lower() or "asyncpg" in url:
        return {"status": "live", "message": "Neon PostgreSQL configured"}
    return {"status": "configured", "message": "Database URL set"}


def _validate_clerk() -> dict:
    """Check Clerk auth keys."""
    secret = os.getenv("CLERK_SECRET_KEY", "")
    pub = os.getenv("CLERK_PUBLISHABLE_KEY", "")
    if secret and pub:
        return {"status": "live", "message": "Clerk auth configured"}
    return {"status": "missing", "message": "Clerk keys not set — auth disabled"}


@router.get("/status")
async def config_status():
    """
    Returns the health/validation status of all external integrations.
    Use this to verify which APIs are configured and working.
    """
    groq = await _validate_groq()
    whatsapp = await _validate_whatsapp()
    twilio = await _validate_twilio()
    vapi = await _validate_vapi()
    database = _validate_database()
    clerk = _validate_clerk()

    integrations = {
        "groq_ai": groq,
        "whatsapp": whatsapp,
        "twilio": twilio,
        "vapi_voice": vapi,
        "database": database,
        "clerk_auth": clerk,
    }

    live_count = sum(1 for v in integrations.values() if v["status"] == "live")
    total = len(integrations)

    return {
        "overall": f"{live_count}/{total} integrations live",
        "ready_for_demo": live_count >= 3,  # At minimum: groq + database + one channel
        "integrations": integrations,
    }


def print_startup_status():
    """Print a clear config status table on startup."""
    checks = {
        "Groq AI": _check_env("GROQ_API_KEY"),
        "Database": _check_env("DATABASE_URL"),
        "Clerk Auth": _check_env("CLERK_SECRET_KEY"),
        "WhatsApp Token": _check_env("WHATSAPP_TOKEN"),
        "WhatsApp Phone ID": _check_env("WHATSAPP_PHONE_NUMBER_ID"),
        "Twilio SID": _check_env("TWILIO_ACCOUNT_SID"),
        "Twilio Token": _check_env("TWILIO_AUTH_TOKEN"),
        "Twilio Phone": _check_env("TWILIO_PHONE_NUMBER"),
        "Vapi API Key": _check_env("VAPI_API_KEY"),
        "Vapi Assistant": _check_env("VAPI_ASSISTANT_ID"),
    }

    print("\n" + "═" * 55)
    print("  SwasthAI — Integration Status")
    print("═" * 55)
    for name, ok in checks.items():
        icon = "✅" if ok else "❌"
        print(f"  {icon}  {name}")
    
    live = sum(1 for v in checks.values() if v)
    print("─" * 55)
    print(f"  {live}/{len(checks)} configured  │  GET /api/config/status for details")
    print("═" * 55 + "\n")

"""
api/whatsapp.py — Meta WhatsApp Cloud API Webhook
==================================================
Handles:
  GET  /webhook/whatsapp  — Meta verification challenge
  POST /webhook/whatsapp  — Incoming messages
"""
import os
import json
import httpx
from fastapi import APIRouter, Request, Response, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from models.models import Case
from engine import ai_engine, session as sess
from engine.outbreak import detect_outbreaks
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/webhook", tags=["WhatsApp"])

WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "swasthai_webhook_verify_2024")
GRAPH_API_URL = f"https://graph.facebook.com/v19.0/{WHATSAPP_PHONE_NUMBER_ID}/messages"


# ── Verification (Meta calls this when you set up webhook) ─────

@router.get("/whatsapp")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("[WhatsApp] ✅ Webhook verified by Meta")
        return Response(content=challenge, media_type="text/plain")

    raise HTTPException(status_code=403, detail="Verification failed")


# ── Incoming Messages ──────────────────────────────────────────

@router.post("/whatsapp")
async def receive_message(
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        body = await request.json()
    except Exception:
        return {"status": "ok"}

    # Extract message from Meta payload structure
    try:
        entry = body["entry"][0]
        change = entry["changes"][0]
        value = change["value"]

        if "messages" not in value:
            return {"status": "ok"}  # status updates, not messages

        message = value["messages"][0]
        from_number = message["from"]
        msg_type = message.get("type", "")

        if msg_type == "text":
            user_text = message["text"]["body"]
        elif msg_type == "audio":
            # Audio messages — ask user to type
            await _send_whatsapp(from_number, "🙏 Namaste! Abhi hum audio nahi samajh sakte. Kripya apni takleef type karke likhein.\n\n🙏 Please type your symptoms in text.")
            return {"status": "ok"}
        else:
            return {"status": "ok"}

    except (KeyError, IndexError):
        return {"status": "ok"}

    # Handle "new" or "reset" keywords
    if user_text.strip().lower() in ["new", "reset", "start", "hi", "hello", "namaste", "नमस्ते"]:
        sess.clear_session(from_number)
        greeting = (
            "🙏 *SwasthAI में आपका स्वागत है!*\n\n"
            "मैं आपकी स्वास्थ्य समस्या में मदद करूंगा। "
            "कृपया अपनी तकलीफ बताएं — जैसे बुखार, खांसी, पेट दर्द, आदि।\n\n"
            "---\n"
            "🙏 *Welcome to SwasthAI!*\n\n"
            "I'll help you understand your health concern. "
            "Please describe your symptoms — like fever, cough, stomach pain, etc."
        )
        await _send_whatsapp(from_number, greeting)
        return {"status": "ok"}

    # Check if session is completed — suggest new
    if sess.is_completed(from_number):
        await _send_whatsapp(
            from_number,
            "✅ Your previous assessment is complete.\n"
            "Type *new* to start a fresh consultation.\n\n"
            "✅ आपकी पिछली जांच पूरी हो गई है।\n"
            "नई जांच के लिए *new* लिखें।"
        )
        return {"status": "ok"}

    # Add user message to session
    sess.add_message(from_number, "user", user_text)
    messages = sess.get_messages(from_number)
    force = sess.should_force_assess(from_number)

    # Run AI engine
    assessment = await ai_engine.analyze_symptoms(messages, force_assess=force)

    if assessment.get("assessment"):
        # Final assessment — format & send
        reply = ai_engine.format_whatsapp_response(assessment)
        await _send_whatsapp(from_number, reply)
        sess.add_message(from_number, "assistant", reply)
        sess.mark_completed(from_number)

        # Save case to DB + trigger outbreak detection in background
        await _save_case(db, from_number, assessment, user_text)
        background_tasks.add_task(_run_outbreak_check)

    else:
        # Follow-up question
        question = assessment.get("follow_up_question", "Please describe your symptoms.")
        await _send_whatsapp(from_number, question)
        sess.add_message(from_number, "assistant", question)

    return {"status": "ok"}


async def _run_outbreak_check():
    """Background task: run outbreak detection after a case is saved."""
    from models.database import AsyncSessionLocal
    try:
        async with AsyncSessionLocal() as db:
            new_alerts = await detect_outbreaks(db)
            if new_alerts:
                print(f"[Outbreak] 🚨 Auto-detected {len(new_alerts)} new alert(s) after case save")
    except Exception as e:
        print(f"[Outbreak] Background check error: {e}")



async def _send_whatsapp(to: str, text: str):
    """Send a WhatsApp message via Meta Cloud API."""
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
        print(f"[WhatsApp] MOCK → {to}: {text[:80]}...")
        return

    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text, "preview_url": False},
    }
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(GRAPH_API_URL, json=payload, headers=headers)
        if resp.status_code != 200:
            print(f"[WhatsApp] ❌ Send error {resp.status_code}: {resp.text}")


async def _save_case(db: AsyncSession, phone: str, assessment: dict, raw_input: str):
    """Persist the completed case to DB."""
    import json
    case = Case(
        phone=phone,
        channel="whatsapp",
        language=assessment.get("language", "en"),
        symptoms=json.dumps(assessment.get("symptoms_extracted", [])),
        risk_level=assessment.get("risk_level", "mild"),
        conditions=json.dumps(assessment.get("possible_conditions", [])),
        recommendation=assessment.get("recommendation"),
        seek_emergency=assessment.get("seek_emergency", False),
        home_care_tips=json.dumps(assessment.get("home_care_tips", [])),
        raw_input=raw_input,
    )
    db.add(case)
    await db.commit()
    print(f"[DB] ✅ Case saved — {phone} | {assessment.get('risk_level')}")

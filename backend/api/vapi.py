"""
api/vapi.py — Vapi Voice Agent Webhook (Custom LLM Endpoint)
=============================================================
Vapi calls this endpoint as your "custom LLM" during voice calls.
It receives the conversation history and returns the assistant's next response.

Twilio → Vapi → POST /webhook/vapi → Groq → response → Vapi TTS → Caller

Also handles call events: call-started, call-ended (for DB logging).
"""
import os
import json
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from models.database import get_db
from models.models import Case
from engine import ai_engine
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/webhook", tags=["Vapi Voice"])


@router.post("/vapi")
async def vapi_custom_llm(request: Request, db: AsyncSession = Depends(get_db)):
    """
    Vapi Custom LLM endpoint.
    Receives OpenAI-compatible message format, returns streaming or non-streaming response.
    We return non-streaming JSON for simplicity.
    """
    try:
        body = await request.json()
    except Exception:
        return {"role": "assistant", "content": "I'm sorry, I couldn't understand that. Please try again."}

    message_type = body.get("message", {}).get("type", "")

    # ── Call lifecycle events ────────────────────────────────
    if message_type == "conversation-update":
        # Vapi sends conversation updates — ignore
        return {"result": "ok"}

    if message_type == "end-of-call-report":
        # Call ended — save case summary
        conversation = body.get("message", {}).get("artifact", {}).get("messages", [])
        call_id = body.get("message", {}).get("call", {}).get("id", "unknown")
        await _save_call_case(db, call_id, conversation)
        return {"result": "ok"}

    # ── Custom LLM request (main flow) ───────────────────────
    messages = body.get("messages", [])

    # Filter to user/assistant messages only
    conversation = [m for m in messages if m.get("role") in ("user", "assistant")]

    if not conversation:
        return {
            "role": "assistant",
            "content": "Namaste! Main SwasthAI hoon. Aap mujhe apni takleef batayein — main madad karunga. Hello! I'm SwasthAI. Please tell me your symptoms and I'll help you."
        }

    # Use AI engine with voice-optimized prompt
    turn_count = sum(1 for m in conversation if m.get("role") == "user")
    force_assess = turn_count >= 3

    assessment = await ai_engine.analyze_symptoms(conversation, force_assess=force_assess)

    if assessment.get("assessment"):
        content = _format_voice_response(assessment)
    else:
        content = assessment.get("follow_up_question", "Please tell me more about your symptoms.")

    return {"role": "assistant", "content": content}


def _format_voice_response(assessment: dict) -> str:
    """Format assessment for voice — no markdown, short sentences."""
    lang = assessment.get("language", "en")
    risk = assessment.get("risk_level", "mild")
    emergency = assessment.get("seek_emergency", False)

    if lang == "hi":
        risk_text = {"mild": "हल्की", "moderate": "मध्यम", "critical": "गंभीर"}.get(risk, "")
        conditions = "، ".join(assessment.get("possible_conditions", [])[:2])
        rec = assessment.get("recommendation", "")

        text = f"आपकी जांच पूरी हुई। यह {risk_text} स्वास्थ्य समस्या लग रही है। "
        if conditions:
            text += f"संभावित कारण हो सकता है {conditions}। "
        text += rec
        if emergency:
            text += " कृपया तुरंत 108 पर कॉल करें।"
        else:
            text += " डॉक्टर से जरूर मिलें।"
    else:
        risk_text = {"mild": "mild", "moderate": "moderate", "critical": "serious"}.get(risk, "")
        conditions = " or ".join(assessment.get("possible_conditions", [])[:2])
        rec = assessment.get("recommendation", "")

        text = f"Based on your symptoms, this appears to be a {risk_text} condition. "
        if conditions:
            text += f"It could be {conditions}. "
        text += rec
        if emergency:
            text += " Please call 108 immediately."
        else:
            text += " Please consult a doctor for confirmation."

    return text


async def _save_call_case(db: AsyncSession, call_id: str, conversation: list):
    """Save voice call case after call ends."""
    # Extract user messages as raw input
    user_msgs = [m.get("content", "") for m in conversation if m.get("role") == "user"]
    raw = " | ".join(user_msgs)

    if not raw:
        return

    # Quick re-analysis for structured data
    assessment = await ai_engine.analyze_symptoms(
        [m for m in conversation if m.get("role") in ("user", "assistant")],
        force_assess=True
    )

    case = Case(
        phone=f"call_{call_id[:8]}",
        channel="call",
        language=assessment.get("language", "en"),
        symptoms=json.dumps(assessment.get("symptoms_extracted", [])),
        risk_level=assessment.get("risk_level", "mild"),
        conditions=json.dumps(assessment.get("possible_conditions", [])),
        recommendation=assessment.get("recommendation"),
        seek_emergency=assessment.get("seek_emergency", False),
        home_care_tips=json.dumps(assessment.get("home_care_tips", [])),
        raw_input=raw[:500],
    )
    db.add(case)
    await db.commit()
    print(f"[DB] ✅ Call case saved — {call_id[:8]} | {assessment.get('risk_level')}")

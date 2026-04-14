"""
engine/ai_engine.py — Groq-Powered Symptom Analysis Engine
===========================================================
Uses llama-3.3-70b-versatile to:
  1. Understand symptoms in Hindi or English
  2. Classify risk level: mild | moderate | critical
  3. Return structured JSON with conditions, recommendations, home care
  4. Support multi-turn conversation via message history
"""
import os
import json
import re
import asyncio
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are SwasthAI, an AI health assistant for rural India. 
You help villagers who describe their symptoms via WhatsApp or phone call.
You support both Hindi and English. Detect the language from the user's message and respond in the SAME language.

Your job:
1. Listen to the patient describe their symptoms
2. Ask ONE relevant follow-up question if you need more info (first 1-2 messages)
3. After enough info, provide a health assessment

CRITICAL RULES:
- NEVER claim to diagnose. Always say "possible" or "could be"
- For ANY critical risk, ALWAYS include "Turant 108 call karein" (Call 108 immediately) in Hindi OR "Call 108 immediately" in English
- Always end with: consult a doctor to confirm
- Use simple, rural-friendly language — not medical jargon
- For Hindi: use simple conversational Hindi, not formal Sanskrit-heavy Hindi

After gathering enough symptoms (or by message 3 at latest), respond with ONLY this JSON:
{
  "assessment": true,
  "risk_level": "mild" | "moderate" | "critical",
  "possible_conditions": ["condition1", "condition2"],
  "recommendation": "Clear action steps in patient's language",
  "follow_up_question": null,
  "language": "hi" | "en",
  "symptoms_extracted": ["symptom1", "symptom2"],
  "seek_emergency": true | false,
  "home_care_tips": ["tip1", "tip2", "tip3"]
}

If you're still gathering info (not final assessment yet), respond with:
{
  "assessment": false,
  "follow_up_question": "Your question here in patient's language",
  "language": "hi" | "en"
}

Risk level guide:
- mild: fever < 101°F, common cold, minor ache — home care OK
- moderate: high fever, chest discomfort, persistent vomiting — visit clinic
- critical: severe chest pain, difficulty breathing, unconsciousness, seizure — emergency 108"""


async def analyze_symptoms(messages: list, force_assess: bool = False) -> dict:
    """
    Run Groq LLM on conversation history.
    messages: list of {role: user|assistant, content: str}
    force_assess: if True, force final assessment regardless of turn count
    Returns parsed dict with assessment fields.
    """
    system = SYSTEM_PROMPT
    if force_assess:
        system += "\n\nIMPORTANT: The patient has provided enough information. Give the FINAL ASSESSMENT JSON now. Do not ask more questions."

    try:
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model=MODEL,
            messages=[{"role": "system", "content": system}, *messages],
            temperature=0.3,
            max_tokens=800,
        )
        raw = response.choices[0].message.content.strip()

        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if json_match:
            return json.loads(json_match.group())
        else:
            # Fallback if LLM didn't return JSON
            return {
                "assessment": False,
                "follow_up_question": raw,
                "language": "en"
            }

    except json.JSONDecodeError:
        return {
            "assessment": False,
            "follow_up_question": "Could you describe your symptoms in more detail?",
            "language": "en"
        }
    except Exception as e:
        print(f"[Groq] Error: {e}")
        return {
            "assessment": True,
            "risk_level": "moderate",
            "possible_conditions": ["Unknown - please see a doctor"],
            "recommendation": "We couldn't analyze your symptoms properly. Please visit your nearest health center or call 104.",
            "follow_up_question": None,
            "language": "en",
            "symptoms_extracted": [],
            "seek_emergency": False,
            "home_care_tips": ["Rest well", "Drink plenty of fluids", "Visit a doctor"]
        }


def format_whatsapp_response(assessment: dict) -> str:
    """Format AI assessment into clean WhatsApp message."""
    if not assessment.get("assessment"):
        return assessment.get("follow_up_question", "Please describe your symptoms.")

    lang = assessment.get("language", "en")
    risk = assessment.get("risk_level", "mild")
    emergency = assessment.get("seek_emergency", False)

    if lang == "hi":
        risk_emoji = {"mild": "🟢", "moderate": "🟡", "critical": "🔴"}.get(risk, "🟡")
        risk_text = {"mild": "हल्की समस्या", "moderate": "मध्यम समस्या", "critical": "⚠️ गंभीर स्थिति"}.get(risk, "मध्यम")

        lines = [
            f"*SwasthAI स्वास्थ्य रिपोर्ट* {risk_emoji}",
            f"*स्तर:* {risk_text}",
            "",
            f"*संभावित कारण:*",
        ]
        for cond in assessment.get("possible_conditions", []):
            lines.append(f"• {cond}")

        lines += ["", f"*सलाह:*", assessment.get("recommendation", "")]

        if assessment.get("home_care_tips"):
            lines += ["", "*घरेलू उपाय:*"]
            for tip in assessment.get("home_care_tips", []):
                lines.append(f"• {tip}")

        if emergency:
            lines += ["", "🚨 *तुरंत 108 पर कॉल करें या नजदीकी अस्पताल जाएं!*"]

        lines += ["", "_नोट: यह जानकारी केवल मार्गदर्शन के लिए है। पक्की जानकारी के लिए डॉक्टर से मिलें।_"]

    else:
        risk_emoji = {"mild": "🟢", "moderate": "🟡", "critical": "🔴"}.get(risk, "🟡")
        risk_text = {"mild": "Mild", "moderate": "Moderate", "critical": "⚠️ CRITICAL"}.get(risk, "Moderate")

        lines = [
            f"*SwasthAI Health Report* {risk_emoji}",
            f"*Risk Level:* {risk_text}",
            "",
            f"*Possible Conditions:*",
        ]
        for cond in assessment.get("possible_conditions", []):
            lines.append(f"• {cond}")

        lines += ["", f"*Recommendation:*", assessment.get("recommendation", "")]

        if assessment.get("home_care_tips"):
            lines += ["", "*Home Care Tips:*"]
            for tip in assessment.get("home_care_tips", []):
                lines.append(f"• {tip}")

        if emergency:
            lines += ["", "🚨 *Call 108 immediately or go to the nearest hospital!*"]

        lines += ["", "_Note: This is guidance only. Please consult a doctor for confirmation._"]

    return "\n".join(lines)


def format_vapi_system_prompt() -> str:
    """Return system prompt for Vapi voice assistant."""
    return """You are SwasthAI, a friendly voice health assistant for rural India.
You speak in simple Hindi or English depending on what the caller uses.
Help people describe their symptoms and give basic health guidance.
Keep responses SHORT (2-3 sentences max) since this is a phone call.
For emergencies, always say: Please call 108 immediately.
Do not use special characters or formatting — just plain speech.
After gathering symptoms (2-3 exchanges), give a brief assessment and recommend whether to:
1. Rest at home with simple remedies
2. Visit the nearest health center  
3. Call 108 emergency immediately"""

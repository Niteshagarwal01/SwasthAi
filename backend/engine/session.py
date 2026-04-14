"""
engine/session.py — Multi-turn Conversation Session Manager
============================================================
Tracks conversation history per phone number (in-memory + DB backup).
Sessions expire after 15 minutes of inactivity.
"""
import json
from datetime import datetime, timedelta
from typing import Optional

# In-memory session store: { phone: {messages, channel, updated_at} }
_sessions: dict = {}
SESSION_TIMEOUT_MINUTES = 15
MAX_TURNS_BEFORE_FORCE_ASSESS = 3


def get_session(phone: str) -> dict:
    """Get or create a session for a phone number."""
    now = datetime.utcnow()

    if phone in _sessions:
        session = _sessions[phone]
        # Check timeout
        if now - session["updated_at"] > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
            del _sessions[phone]
        else:
            return session

    # New session
    _sessions[phone] = {
        "phone": phone,
        "messages": [],
        "turn_count": 0,
        "channel": "whatsapp",
        "updated_at": now,
        "completed": False,
    }
    return _sessions[phone]


def add_message(phone: str, role: str, content: str):
    """Add a message to the session history."""
    session = get_session(phone)
    session["messages"].append({"role": role, "content": content})
    session["updated_at"] = datetime.utcnow()
    if role == "user":
        session["turn_count"] += 1


def should_force_assess(phone: str) -> bool:
    """Return True if we've asked enough questions and should force final assessment."""
    session = _sessions.get(phone, {})
    return session.get("turn_count", 0) >= MAX_TURNS_BEFORE_FORCE_ASSESS


def get_messages(phone: str) -> list:
    """Return conversation history for Groq."""
    session = _sessions.get(phone, {})
    return session.get("messages", [])


def mark_completed(phone: str):
    """Mark session as completed (assessment delivered)."""
    if phone in _sessions:
        _sessions[phone]["completed"] = True


def clear_session(phone: str):
    """Clear session (new conversation)."""
    if phone in _sessions:
        del _sessions[phone]


def is_completed(phone: str) -> bool:
    return _sessions.get(phone, {}).get("completed", False)


def get_turn_count(phone: str) -> int:
    return _sessions.get(phone, {}).get("turn_count", 0)

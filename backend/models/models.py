"""
models/models.py — SQLAlchemy ORM Models + Pydantic Schemas
Tables: cases, alerts, sessions
"""
import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Text, Boolean, Integer, DateTime, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column
from pydantic import BaseModel, Field
from models.database import Base


# ─────────────────────────────────────────────────────────────
# SQLAlchemy ORM Models
# ─────────────────────────────────────────────────────────────

class Case(Base):
    __tablename__ = "cases"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    channel: Mapped[str] = mapped_column(String(10), default="whatsapp")      # whatsapp | call
    language: Mapped[str] = mapped_column(String(5), default="en")             # hi | en
    region: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # state/district
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Symptom & AI output
    symptoms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)        # JSON list stored as text
    risk_level: Mapped[str] = mapped_column(String(10), default="mild")         # mild | moderate | critical
    conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)      # JSON list
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    seek_emergency: Mapped[bool] = mapped_column(Boolean, default=False)
    home_care_tips: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON list

    # Raw conversation
    raw_input: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    region: Mapped[str] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    symptom_cluster: Mapped[str] = mapped_column(Text)   # JSON list
    case_count: Mapped[int] = mapped_column(Integer, default=0)
    severity: Mapped[str] = mapped_column(String(10), default="medium")  # low | medium | high | critical
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Session(Base):
    __tablename__ = "sessions"

    phone: Mapped[str] = mapped_column(String(20), primary_key=True)
    channel: Mapped[str] = mapped_column(String(10), default="whatsapp")
    messages: Mapped[str] = mapped_column(Text, default="[]")   # JSON array of {role, content}
    symptom_count: Mapped[int] = mapped_column(Integer, default=0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


# ─────────────────────────────────────────────────────────────
# Pydantic Response Schemas
# ─────────────────────────────────────────────────────────────

class CaseOut(BaseModel):
    id: str
    phone: Optional[str]
    channel: str
    language: str
    region: Optional[str]
    state: Optional[str]
    symptoms: Optional[List[str]]
    risk_level: str
    conditions: Optional[List[str]]
    recommendation: Optional[str]
    seek_emergency: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AlertOut(BaseModel):
    id: str
    region: str
    state: Optional[str]
    symptom_cluster: List[str]
    case_count: int
    severity: str
    description: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_cases: int
    cases_today: int
    critical_today: int
    active_regions: int
    active_alerts: int
    whatsapp_cases: int
    call_cases: int
    avg_risk_score: float

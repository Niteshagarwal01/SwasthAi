"""
api/analytics.py — Dashboard Analytics APIs
============================================
Provides all data needed for the admin React dashboard.
All endpoints require Clerk JWT auth (verified via middleware in main.py).
"""
import json
from datetime import datetime, timedelta
from collections import Counter
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from models.database import get_db
from models.models import Case, Alert

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    """KPI cards: total cases, today's cases, critical count, active alerts, etc."""
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Total cases
    total = await db.scalar(select(func.count(Case.id)))

    # Cases today
    today_result = await db.scalar(
        select(func.count(Case.id)).where(Case.created_at >= today)
    )

    # Critical today
    critical_today = await db.scalar(
        select(func.count(Case.id)).where(
            and_(Case.created_at >= today, Case.risk_level == "critical")
        )
    )

    # Active regions (distinct states with cases in last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    active_states_result = await db.execute(
        select(func.count(func.distinct(Case.state))).where(
            and_(Case.created_at >= week_ago, Case.state.isnot(None))
        )
    )
    active_regions = active_states_result.scalar() or 0

    # Active alerts
    active_alerts = await db.scalar(
        select(func.count(Alert.id)).where(Alert.is_active == True)
    )

    # Channel split
    wa_count = await db.scalar(
        select(func.count(Case.id)).where(Case.channel == "whatsapp")
    )
    call_count = await db.scalar(
        select(func.count(Case.id)).where(Case.channel == "call")
    )

    # Emergency cases today
    emergency_today = await db.scalar(
        select(func.count(Case.id)).where(
            and_(Case.created_at >= today, Case.seek_emergency == True)
        )
    )

    return {
        "total_cases": total or 0,
        "cases_today": today_result or 0,
        "critical_today": critical_today or 0,
        "emergency_today": emergency_today or 0,
        "active_regions": active_regions,
        "active_alerts": active_alerts or 0,
        "whatsapp_cases": wa_count or 0,
        "call_cases": call_count or 0,
    }


@router.get("/symptoms")
async def get_top_symptoms(limit: int = Query(10), days: int = Query(30), db: AsyncSession = Depends(get_db)):
    """Top N symptoms by frequency in the last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(Case.symptoms).where(
            and_(Case.created_at >= cutoff, Case.symptoms.isnot(None))
        )
    )
    rows = result.scalars().all()

    symptom_counter = Counter()
    for row in rows:
        try:
            symptoms = json.loads(row)
            for s in symptoms:
                if s:
                    symptom_counter[s.lower().strip()] += 1
        except Exception:
            pass

    top = symptom_counter.most_common(limit)
    return [{"symptom": s, "count": c} for s, c in top]


@router.get("/regional")
async def get_regional(days: int = Query(30), db: AsyncSession = Depends(get_db)):
    """Case counts by state/region with risk level breakdown."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(Case.state, Case.risk_level, func.count(Case.id).label("count"))
        .where(and_(Case.created_at >= cutoff, Case.state.isnot(None)))
        .group_by(Case.state, Case.risk_level)
        .order_by(desc("count"))
    )
    rows = result.all()

    # Aggregate by state
    state_data: dict = {}
    for state, risk, count in rows:
        if state not in state_data:
            state_data[state] = {"state": state, "total": 0, "mild": 0, "moderate": 0, "critical": 0}
        state_data[state]["total"] += count
        state_data[state][risk] = state_data[state].get(risk, 0) + count

    return sorted(state_data.values(), key=lambda x: -x["total"])


@router.get("/timeline")
async def get_timeline(days: int = Query(30), db: AsyncSession = Depends(get_db)):
    """Daily case counts for the last N days."""
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = await db.execute(
        select(Case.created_at, Case.risk_level)
        .where(Case.created_at >= cutoff)
        .order_by(Case.created_at)
    )
    rows = result.all()

    # Group by date
    daily: dict = {}
    for created_at, risk in rows:
        date_str = created_at.strftime("%Y-%m-%d")
        if date_str not in daily:
            daily[date_str] = {"date": date_str, "total": 0, "mild": 0, "moderate": 0, "critical": 0}
        daily[date_str]["total"] += 1
        daily[date_str][risk] = daily[date_str].get(risk, 0) + 1

    # Fill missing dates
    result_list = []
    for i in range(days):
        date = (datetime.utcnow() - timedelta(days=days - i - 1)).strftime("%Y-%m-%d")
        result_list.append(daily.get(date, {"date": date, "total": 0, "mild": 0, "moderate": 0, "critical": 0}))

    return result_list


@router.get("/alerts")
async def get_alerts(db: AsyncSession = Depends(get_db)):
    """Active outbreak alerts."""
    result = await db.execute(
        select(Alert)
        .where(Alert.is_active == True)
        .order_by(desc(Alert.created_at))
        .limit(20)
    )
    alerts = result.scalars().all()

    return [
        {
            "id": a.id,
            "region": a.region,
            "state": a.state,
            "symptom_cluster": json.loads(a.symptom_cluster or "[]"),
            "case_count": a.case_count,
            "severity": a.severity,
            "description": a.description,
            "is_active": a.is_active,
            "created_at": a.created_at.isoformat(),
        }
        for a in alerts
    ]


@router.get("/channels")
async def get_channels(db: AsyncSession = Depends(get_db)):
    """WhatsApp vs Call split + language distribution."""
    result = await db.execute(
        select(Case.channel, Case.language, func.count(Case.id).label("count"))
        .group_by(Case.channel, Case.language)
    )
    rows = result.all()

    channels = {"whatsapp": 0, "call": 0}
    languages = {"hi": 0, "en": 0}

    for channel, lang, count in rows:
        channels[channel] = channels.get(channel, 0) + count
        languages[lang] = languages.get(lang, 0) + count

    return {"channels": channels, "languages": languages}

"""
api/cases.py — Cases CRUD API
"""
import json
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, and_
from models.database import get_db
from models.models import Case

router = APIRouter(prefix="/api/cases", tags=["Cases"])


@router.get("")
async def list_cases(
    page: int = Query(1, ge=1),
    limit: int = Query(20, le=100),
    risk: str = Query(None),
    channel: str = Query(None),
    state: str = Query(None),
    db: AsyncSession = Depends(get_db),
):
    filters = []
    if risk:
        filters.append(Case.risk_level == risk)
    if channel:
        filters.append(Case.channel == channel)
    if state:
        filters.append(Case.state == state)

    offset = (page - 1) * limit
    query = select(Case).order_by(desc(Case.created_at)).offset(offset).limit(limit)
    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query)
    cases = result.scalars().all()

    return [_case_out(c) for c in cases]


@router.get("/{case_id}")
async def get_case(case_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Case).where(Case.id == case_id))
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return _case_out(case)


def _case_out(c: Case) -> dict:
    def _parse(val):
        try:
            return json.loads(val) if val else []
        except Exception:
            return []

    return {
        "id": c.id,
        "phone": c.phone,
        "channel": c.channel,
        "language": c.language,
        "region": c.region,
        "state": c.state,
        "symptoms": _parse(c.symptoms),
        "risk_level": c.risk_level,
        "conditions": _parse(c.conditions),
        "recommendation": c.recommendation,
        "seek_emergency": c.seek_emergency,
        "home_care_tips": _parse(c.home_care_tips),
        "raw_input": c.raw_input,
        "created_at": c.created_at.isoformat() if c.created_at else None,
    }

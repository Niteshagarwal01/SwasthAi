"""
engine/outbreak.py — Outbreak Pattern Detection
================================================
Scans case DB for clusters of same symptoms in same region within 48h.
Fires an Alert record when threshold exceeded.
"""
import json
from datetime import datetime, timedelta
from collections import defaultdict
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.models import Case, Alert

OUTBREAK_THRESHOLD = 5          # cases in same region with same symptom
OUTBREAK_WINDOW_HOURS = 48      # within this window
HIGH_RISK_SYMPTOMS = [
    "fever", "bukhar", "high fever",
    "dengue", "malaria",
    "diarrhea", "dast", "cholera",
    "vomiting", "ulti",
    "rash", "skin rash",
    "jaundice", "peelia",
    "measles", "khasra",
]


async def detect_outbreaks(db: AsyncSession) -> list[dict]:
    """
    Run outbreak detection on recent cases.
    Returns list of new alert dicts (also saved to DB).
    """
    cutoff = datetime.utcnow() - timedelta(hours=OUTBREAK_WINDOW_HOURS)

    # Fetch recent cases with state info
    result = await db.execute(
        select(Case).where(
            and_(Case.created_at >= cutoff, Case.state.isnot(None))
        )
    )
    recent_cases = result.scalars().all()

    # Group by (state, symptom)
    clusters: dict[tuple, list] = defaultdict(list)
    for case in recent_cases:
        try:
            symptoms = json.loads(case.symptoms or "[]")
        except Exception:
            symptoms = []

        for symptom in symptoms:
            symptom_lower = symptom.lower()
            for hs in HIGH_RISK_SYMPTOMS:
                if hs in symptom_lower:
                    clusters[(case.state, hs)].append(case.id)
                    break

    new_alerts = []
    for (state, symptom), case_ids in clusters.items():
        if len(case_ids) >= OUTBREAK_THRESHOLD:
            # Check if alert already exists
            existing = await db.execute(
                select(Alert).where(
                    and_(
                        Alert.state == state,
                        Alert.is_active == True,
                    )
                )
            )
            if existing.scalars().first():
                continue  # Already alerted

            severity = "critical" if len(case_ids) >= OUTBREAK_THRESHOLD * 3 else \
                       "high" if len(case_ids) >= OUTBREAK_THRESHOLD * 2 else "medium"

            alert = Alert(
                region=state,
                state=state,
                symptom_cluster=json.dumps([symptom]),
                case_count=len(case_ids),
                severity=severity,
                description=f"⚠️ {len(case_ids)} cases of '{symptom}' symptoms detected in {state} within 48 hours. Possible outbreak.",
                is_active=True,
            )
            db.add(alert)
            new_alerts.append({
                "region": state,
                "symptom": symptom,
                "count": len(case_ids),
                "severity": severity,
            })

    if new_alerts:
        await db.commit()
        print(f"[Outbreak] 🚨 {len(new_alerts)} new alerts fired")

    return new_alerts

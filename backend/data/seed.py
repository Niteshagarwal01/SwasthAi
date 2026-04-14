"""
data/seed.py — Demo Data Seeder
================================
Generates 500+ realistic rural India health cases for dashboard demo.
Run: python -m data.seed
Or called automatically on first startup in dev mode.
"""
import json
import random
import asyncio
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from models.database import AsyncSessionLocal, init_db
from models.models import Case, Alert
from sqlalchemy import select, func

# ── Indian States ─────────────────────────────────────────────
STATES = [
    "Uttar Pradesh", "Bihar", "Rajasthan", "Madhya Pradesh",
    "Maharashtra", "West Bengal", "Odisha", "Jharkhand",
    "Chhattisgarh", "Gujarat", "Haryana", "Punjab",
]

DISTRICTS = {
    "Uttar Pradesh": ["Varanasi", "Lucknow", "Gorakhpur", "Agra", "Kanpur"],
    "Bihar": ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Bikaner", "Udaipur", "Kota"],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Rewa"],
    "Maharashtra": ["Nashik", "Aurangabad", "Amravati", "Nanded", "Solapur"],
    "West Bengal": ["Kolkata", "Howrah", "Murshidabad", "Malda", "Purnia"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Sambalpur", "Berhampur", "Puri"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh"],
    "Chhattisgarh": ["Raipur", "Bilaspur", "Korba", "Durg", "Raigarh"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar"],
    "Haryana": ["Faridabad", "Gurgaon", "Hisar", "Rohtak", "Panipat"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda"],
}

# ── Symptom / Condition Profiles ──────────────────────────────
CASE_PROFILES = [
    # (weight, risk, symptoms, conditions, language, emergency, home_tips)
    (15, "mild", ["fever", "body ache", "headache"], ["Viral fever", "Common flu"], "en", False,
     ["Rest well", "Drink lots of water", "Take paracetamol"]),
    (15, "mild", ["bukhar", "sar dard", "khansee"], ["Viral bukhar", "Sardi"], "hi", False,
     ["Aaram karo", "Paani piyo", "Paracetamol lo"]),
    (10, "moderate", ["high fever", "chills", "joint pain", "sweating"], ["Malaria", "Dengue fever"], "en", False,
     ["Consult doctor urgently", "Stay hydrated", "Use mosquito net"]),
    (10, "moderate", ["tez bukhar", "kaampna", "jodo mein dard"], ["Malaria", "Dengue"], "hi", False,
     ["Doctor se milo", "Paani piyo", "Machhar se bacho"]),
    (8, "moderate", ["cough", "cold", "breathlessness", "chest tightness"], ["Asthma", "Bronchitis", "Chest infection"], "en", False,
     ["Use inhaler if prescribed", "Steam inhalation", "Avoid dust"]),
    (8, "moderate", ["dast", "ulti", "pet dard", "kamzori"], ["Gastroenteritis", "Food poisoning", "Cholera"], "hi", False,
     ["ORS piyo", "Saaf paani piyo", "Doctor se milo"]),
    (5, "critical", ["severe chest pain", "difficulty breathing", "left arm pain"], ["Heart attack", "Angina", "Pulmonary embolism"], "en", True,
     ["Call 108 immediately", "Do not eat or drink", "Lie down"]),
    (5, "critical", ["seene mein dard", "saans lene mein takleef"], ["Dil ka dora", "Angina"], "hi", True,
     ["Turant 108 call karo", "Aaram karo", "Kuch mat khao piyo"]),
    (6, "moderate", ["stomach pain", "vomiting", "nausea", "loose motions"], ["Food poisoning", "Gastritis", "Appendicitis"], "en", False,
     ["Drink ORS", "Eat light food (khichdi)", "Rest"]),
    (4, "critical", ["unconscious", "seizure", "not responding"], ["Epilepsy", "Stroke", "Hypoglycemia"], "en", True,
     ["Call 108 immediately", "Clear airway", "Keep on side"]),
    (4, "moderate", ["skin rash", "itching", "swelling on body", "hives"], ["Allergic reaction", "Urticaria", "Dengue rash"], "en", False,
     ["Antihistamine tablet", "Avoid scratching", "See doctor"]),
    (6, "mild", ["headache", "eye pain", "sensitivity to light"], ["Migraine", "Eye strain", "Tension headache"], "en", False,
     ["Rest in dark room", "Cold compress on forehead", "Avoid screens"]),
    (5, "moderate", ["pilu ka dard", "pet phula hua", "peelia"], ["Jaundice", "Hepatitis", "Liver problem"], "hi", False,
     ["Doctor se milo", "Ghee tel bandh karo", "Halka khana khao"]),
    (4, "critical", ["snake bite", "numbness", "swelling spreading"], ["Snakebite venomation"], "en", True,
     ["Call 108 immediately", "Keep limb still and below heart", "Do not cut or suck"]),
    (5, "mild", ["cold", "runny nose", "sneezing", "mild sore throat"], ["Common cold", "Allergic rhinitis"], "en", False,
     ["Steam inhalation", "Honey ginger tea", "Rest"]),
    (4, "moderate", ["child fever high", "rash on body", "red eyes"], ["Measles", "Rubella", "Dengue"], "en", False,
     ["Visit doctor urgently", "Give paracetamol", "Keep child hydrated"]),
    (3, "moderate", ["bachche ko tez bukhar", "daane nikle hain"], ["Khasra", "Chickenpox", "Dengue"], "hi", False,
     ["Doctor ke paas lo", "Paracetamol do", "Paani pilao"]),
    (4, "mild", ["back pain", "lower back ache", "difficulty standing"], ["Muscle strain", "Sciatica", "Kidney stone"], "en", False,
     ["Hot compress", "Rest", "Avoid heavy lifting"]),
    (3, "critical", ["heavy bleeding", "accident injury", "deep wound"], ["Trauma", "Hemorrhage"], "en", True,
     ["Call 108 immediately", "Apply pressure on wound", "Keep patient still"]),
    (5, "moderate", ["sugar zyada ho gaya", "chakkar aa raha", "haath kaanpna"], ["Diabetes complication", "Hypoglycemia"], "hi", False,
     ["Doctor se milo", "Meetha khao abhi", "Dawai lo"]),
]

WEIGHTS = [p[0] for p in CASE_PROFILES]
TOTAL_WEIGHT = sum(WEIGHTS)


def _pick_profile():
    r = random.uniform(0, TOTAL_WEIGHT)
    acc = 0
    for profile in CASE_PROFILES:
        acc += profile[0]
        if r <= acc:
            return profile
    return CASE_PROFILES[0]


def _random_phone():
    prefixes = ["91", "91", "91"]
    prefix = random.choice(prefixes)
    number = "".join([str(random.randint(0, 9)) for _ in range(10)])
    return f"+{prefix}{number}"


def _random_time(days_back: int = 30) -> datetime:
    """Random datetime in last days_back days, weighted toward recent."""
    # Exponential-ish distribution: more recent cases more common
    r = random.expovariate(0.1)
    days_ago = min(r, days_back)
    hours_ago = days_ago * 24
    return datetime.utcnow() - timedelta(hours=hours_ago)


async def seed_if_empty():
    """Seed only if cases table is empty."""
    async with AsyncSessionLocal() as db:
        count = await db.scalar(select(func.count(Case.id)))
        if count and count > 0:
            print(f"[Seed] DB already has {count} cases — skipping seed")
            return
        await _seed(db)


async def _seed(db):
    """Insert 520 demo cases and 6 fake outbreak alerts."""
    print("[Seed] 🌱 Seeding demo data...")
    n_cases = 520

    cases_to_insert = []
    for i in range(n_cases):
        profile = _pick_profile()
        _, risk, symptoms, conditions, lang, emergency, tips = profile

        state = random.choice(STATES)
        district = random.choice(DISTRICTS.get(state, ["Rural"]))
        channel = random.choices(["whatsapp", "call"], weights=[70, 30])[0]

        case = Case(
            phone=_random_phone(),
            channel=channel,
            language=lang,
            region=district,
            state=state,
            symptoms=json.dumps(symptoms),
            risk_level=risk,
            conditions=json.dumps(conditions),
            recommendation=f"Visit nearest health center. {conditions[0]} suspected.",
            seek_emergency=emergency,
            home_care_tips=json.dumps(tips),
            raw_input=" ".join(symptoms),
            created_at=_random_time(30),
        )
        cases_to_insert.append(case)

    db.add_all(cases_to_insert)

    # Add some recent surge (last 2 days) to make graphs interesting
    for i in range(80):
        profile = _pick_profile()
        _, risk, symptoms, conditions, lang, emergency, tips = profile
        state = random.choice(["Uttar Pradesh", "Bihar", "Rajasthan"])
        district = random.choice(DISTRICTS[state])

        case = Case(
            phone=_random_phone(),
            channel=random.choices(["whatsapp", "call"], weights=[75, 25])[0],
            language=lang,
            region=district,
            state=state,
            symptoms=json.dumps(symptoms),
            risk_level=risk,
            conditions=json.dumps(conditions),
            recommendation=f"Consult a doctor. {conditions[0]} possible.",
            seek_emergency=emergency,
            home_care_tips=json.dumps(tips),
            raw_input=" ".join(symptoms),
            created_at=_random_time(2),  # last 48h
        )
        db.add(case)

    # Seed outbreak alerts
    alerts = [
        Alert(region="Gorakhpur", state="Uttar Pradesh", symptom_cluster=json.dumps(["fever", "joint pain"]),
              case_count=23, severity="high", description="⚠️ 23 cases of fever + joint pain detected in Gorakhpur in 48h — possible Dengue outbreak. Health authorities alerted.", is_active=True),
        Alert(region="Muzaffarpur", state="Bihar", symptom_cluster=json.dumps(["high fever", "chills"]),
              case_count=18, severity="critical", description="🚨 18 cases of high fever with chills in Muzaffarpur — possible Malaria cluster. Immediate intervention needed.", is_active=True),
        Alert(region="Darbhanga", state="Bihar", symptom_cluster=json.dumps(["diarrhea", "vomiting"]),
              case_count=12, severity="medium", description="⚠️ 12 GI illness cases in Darbhanga — possible water contamination. Water testing ordered.", is_active=True),
        Alert(region="Bikaner", state="Rajasthan", symptom_cluster=json.dumps(["skin rash", "fever"]),
              case_count=8, severity="medium", description="8 rash + fever cases in Bikaner — monitoring for Measles.", is_active=True),
        Alert(region="Sambalpur", state="Odisha", symptom_cluster=json.dumps(["jaundice"]),
              case_count=7, severity="high", description="7 jaundice cases in Sambalpur — Hepatitis A screening initiated.", is_active=True),
        Alert(region="Korba", state="Chhattisgarh", symptom_cluster=json.dumps(["fever", "headache"]),
              case_count=6, severity="low", description="6 fever + headache cases in Korba — monitoring for Typhoid.", is_active=True),
    ]
    db.add_all(alerts)

    await db.commit()
    print(f"[Seed] ✅ {n_cases + 80} cases + 6 alerts seeded successfully!")


if __name__ == "__main__":
    asyncio.run(init_db())
    async def run():
        async with AsyncSessionLocal() as db:
            await _seed(db)
    asyncio.run(run())

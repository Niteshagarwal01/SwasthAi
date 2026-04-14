"""
api/main.py — SwasthAI FastAPI Application
==========================================
Entry point. Start: uvicorn api.main:app --reload --port 8000
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

load_dotenv()

from models.database import init_db, get_db
from api.whatsapp import router as whatsapp_router
from api.vapi import router as vapi_router
from api.analytics import router as analytics_router
from api.cases import router as cases_router
from api.config_validator import router as config_router, print_startup_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: init DB tables, seed demo data, print config status."""
    await init_db()

    # Seed demo data if DB is empty
    if os.getenv("APP_ENV", "development") == "development":
        try:
            from data.seed import seed_if_empty
            await seed_if_empty()
        except Exception as e:
            print(f"[Seed] Warning: {e}")

    # Print integration status on every startup
    print_startup_status()

    yield
    print("[App] Shutting down...")


app = FastAPI(
    title="SwasthAI API",
    description="Rural Health Assistant — WhatsApp + Voice + Admin Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow frontend dev + production
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        FRONTEND_URL,
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Routers ───────────────────────────────────────────────────
app.include_router(whatsapp_router)
app.include_router(vapi_router)
app.include_router(analytics_router)
app.include_router(cases_router)
app.include_router(config_router)


# ── Health ────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {
        "service": "SwasthAI Backend",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "channels": ["whatsapp", "voice"],
    }


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "groq": bool(os.getenv("GROQ_API_KEY")),
        "whatsapp": bool(os.getenv("WHATSAPP_TOKEN")),
        "twilio": bool(os.getenv("TWILIO_ACCOUNT_SID")),
        "vapi": bool(os.getenv("VAPI_API_KEY")),
        "config_detail": "/api/config/status",
    }


# ── Outbreak Scan (manual trigger) ────────────────────────────
@app.post("/api/outbreak/scan")
async def trigger_outbreak_scan(db: AsyncSession = Depends(get_db)):
    """
    Manually trigger outbreak detection scan.
    Normally runs automatically after each case is saved.
    Useful for testing and scheduled jobs.
    """
    from engine.outbreak import detect_outbreaks
    new_alerts = await detect_outbreaks(db)
    return {
        "status": "ok",
        "new_alerts": len(new_alerts),
        "alerts": new_alerts,
    }


# ── Simulate WhatsApp message (dev/demo only) ─────────────────
@app.post("/api/simulate/whatsapp")
async def simulate_whatsapp(request: Request):
    """
    Dev endpoint to test the WhatsApp flow without a real Meta account.
    POST { "phone": "+911234567890", "message": "mujhe bukhar hai" }
    """
    body = await request.json()
    phone = body.get("phone", "+910000000000")
    message_text = body.get("message", "I have fever")

    from engine import session as sess, ai_engine

    if message_text.lower() in ["new", "reset"]:
        sess.clear_session(phone)
        return {"reply": "Session reset. Send your symptoms."}

    sess.add_message(phone, "user", message_text)
    messages = sess.get_messages(phone)
    force = sess.should_force_assess(phone)

    assessment = await ai_engine.analyze_symptoms(messages, force_assess=force)

    if assessment.get("assessment"):
        reply = ai_engine.format_whatsapp_response(assessment)
        sess.add_message(phone, "assistant", reply)
        sess.mark_completed(phone)
    else:
        reply = assessment.get("follow_up_question", "Please describe your symptoms.")
        sess.add_message(phone, "assistant", reply)

    return {"reply": reply, "assessment": assessment}

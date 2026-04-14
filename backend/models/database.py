"""
models/database.py — Neon PostgreSQL Async Setup
SQLAlchemy 2.0 async engine + session factory
"""
import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "")

if DATABASE_URL.startswith("postgresql+asyncpg"):
    # Strip any ssl/sslmode params from URL (asyncpg handles SSL differently)
    clean_url = DATABASE_URL.split("?")[0]

    # Create SSL context for Neon
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    engine = create_async_engine(
        clean_url,
        echo=False,
        pool_size=5,
        max_overflow=10,
        connect_args={"ssl": ssl_context},
    )
else:
    # SQLite fallback for dev without Neon
    engine = create_async_engine(
        "sqlite+aiosqlite:///./swasthai_dev.db",
        echo=False,
        connect_args={"check_same_thread": False},
    )

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    """FastAPI dependency — yields async DB session.
    
    NOTE: Callers must explicitly commit(). No auto-commit here
    to prevent double-commit conflicts with webhook handlers.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Create all tables on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[DB] Tables ready on Neon PostgreSQL")

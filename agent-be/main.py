"""
FastAPI application entrypoint.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import close_db
from routers import chat, sessions, certificates
from agent.agent import checkpointer
from agent.memory_manager import cleanup_idle_sessions
import schemas

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: launch background cleanup task. Shutdown: close DB."""
    logger.info("Starting AI Certificate Operations Agent backend...")
    cleanup_task = asyncio.create_task(cleanup_idle_sessions(checkpointer))
    logger.info("Session cleanup background task started (TTL=15min, interval=60s)")
    yield
    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    await close_db()
    logger.info("Shutdown complete.")


app = FastAPI(
    title="AI Certificate Operations Agent",
    description="AI Agent API for enterprise certificate management operations.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(certificates.router)


@app.get("/health", response_model=schemas.HealthResponse, tags=["health"])
async def health():
    return {"status": "ok", "model": settings.openrouter_model}

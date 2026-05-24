"""
FastAPI application entrypoint.

Registers exception handlers, timing middlewares, routing, and handles database lifecycle.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as api_v1_router
from app.config import get_settings
from app.core.exceptions import BaseAppException
from app.core.logging import configure_logging, logger
from app.core.middleware import (
    TimingMiddleware,
    app_exception_handler,
    general_exception_handler,
)
from app.database import close_db, init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles startup and shutdown database lifecycles."""
    # 1. Startup Actions
    configure_logging()
    logger.info(
        "Starting InsightFlow API Server",
        version=settings.app_version,
        environment=settings.environment,
    )
    
    # Initialize DB (create tables for SQLite locally, setup PostgreSQL schemas)
    await init_db()
    
    yield
    
    # 2. Shutdown Actions
    logger.info("Stopping InsightFlow API Server")
    await close_db()


# Create FastAPI App instance
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="InsightFlow AI-Powered Business Intelligence Platform API",
    lifespan=lifespan,
)

# ── Middlewares ──────────────────────────────────────────────────

# 1. Timing and logging middleware
app.add_middleware(TimingMiddleware)

# 2. CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception Handlers ───────────────────────────────────────────

app.add_exception_handler(BaseAppException, app_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, general_exception_handler)


# ── Routing ──────────────────────────────────────────────────────

app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint for deployments."""
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }


@app.get("/", tags=["System"])
async def root():
    """Welcome root message."""
    return {
        "message": "Welcome to the InsightFlow Business Intelligence API.",
        "docs_url": "/docs",
    }

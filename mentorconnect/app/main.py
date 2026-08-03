"""
app/main.py
-------------
FastAPI application entrypoint. Wires together:
- App metadata & Swagger/OpenAPI docs configuration
- CORS, CSRF, security headers, request logging middleware
- Rate limiting (slowapi)
- Global exception handlers
- The v1 API router (all feature endpoints)
- Static file serving for uploaded content (profile images, documents, chat attachments)
- Startup seeding of RBAC roles + Super Admin account

Run locally with:  uvicorn app.main:app --reload
Run in production via Docker: see Dockerfile / docker-compose.yml (gunicorn + uvicorn workers)
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.core.config import settings
from app.core.logger import logger
from app.middlewares.rate_limiter import limiter
from app.middlewares.exception_handler import register_exception_handlers
from app.middlewares.csrf import CSRFMiddleware
from app.middlewares.security_headers import SecurityHeadersMiddleware
from app.middlewares.request_logger import RequestLoggingMiddleware
from app.api.v1.router import api_router
from app.db.seed import run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------------- Startup ----------------
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    try:
        run_seed()
    #except Exception as exc:
        # Don't crash the whole app if seeding fails (e.g. DB not ready yet on first
        # docker-compose up) - migrations/health checks should be retried by the operator.
     #   logger.error(f"Database seeding failed on startup: {exc}")
    #yield

    from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")

    try:
        run_seed()
    except Exception:
        logger.exception("Database seeding failed on startup")
        raise

    yield

    logger.info(f"Shutting down {settings.APP_NAME}...")
    # ---------------- Shutdown ----------------
    logger.info(f"Shutting down {settings.APP_NAME}...")


app = FastAPI(
    title="MentorConnect API",
    description=(
        "MentorConnect - a mentorship matchmaking platform connecting students "
        "with verified mentors. Provides authentication (JWT + refresh tokens), "
        "role-based access control (Super Admin / Mentor / Student), mentor "
        "discovery & search, mentorship request workflows, slot booking, chat, "
        "ratings, complaints, notifications, and admin analytics."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Rate limiting (slowapi)
# ---------------------------------------------------------------------------
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ---------------------------------------------------------------------------
# Middleware (order matters: added LAST runs FIRST on the request path)
# ---------------------------------------------------------------------------
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFMiddleware)
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# ---------------------------------------------------------------------------
# Global exception handlers
# ---------------------------------------------------------------------------
register_exception_handlers(app)

# ---------------------------------------------------------------------------
# Static file serving for uploaded content (profile images, documents, chat files)
# In production, prefer serving these via Nginx/S3/CDN directly rather than FastAPI.
# ---------------------------------------------------------------------------
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health", tags=["Health"], summary="Health check endpoint")
def health_check():
    """Simple liveness probe used by Docker/load balancers/uptime monitors."""
    return {"status": "ok", "service": settings.APP_NAME, "environment": settings.APP_ENV}


@app.get("/", tags=["Health"], summary="API root")
def root():
    return {
        "message": f"Welcome to the {settings.APP_NAME} API.",
        "docs": "/docs",
        "health": "/health",
    }

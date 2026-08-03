# ==========================================================
# MentorConnect Backend - Dockerfile
# Multi-stage build: keeps the final image lean by not shipping build tools.
# ==========================================================

# ---------------- Stage 1: Builder ----------------
FROM python:3.12-slim AS builder

WORKDIR /build

# System packages needed only to COMPILE Python deps (e.g. cryptography, Pillow)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ---------------- Stage 2: Runtime ----------------
FROM python:3.12-slim

WORKDIR /app

# Runtime-only system packages (no compilers needed here)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    default-mysql-client \
    fonts-dejavu-core \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user to run the app (security best practice)
RUN groupadd -r mentorconnect && useradd -r -g mentorconnect mentorconnect

# Copy installed Python packages from the builder stage
COPY --from=builder /root/.local /home/mentorconnect/.local
ENV PATH=/home/mentorconnect/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy application source
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .
COPY docker-entrypoint.sh .

# Create writable directories for uploads/logs and hand ownership to the app user
RUN mkdir -p uploads/profiles uploads/documents uploads/chat logs \
    && chmod +x docker-entrypoint.sh \
    && chown -R mentorconnect:mentorconnect /app /home/mentorconnect/.local

USER mentorconnect

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]

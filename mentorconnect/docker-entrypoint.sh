#!/bin/sh
# ==========================================================
# docker-entrypoint.sh
# Waits for the database to be reachable, runs Alembic migrations,
# then starts the application server (gunicorn + uvicorn workers).
# ==========================================================
set -e

echo "Waiting for MySQL at ${DB_HOST}:${DB_PORT}..."
ATTEMPTS=0
MAX_ATTEMPTS=30
until mysqladmin ping -h "$DB_HOST" -P "$DB_PORT" -u "$DB_USER" -p"$DB_PASSWORD" --silent 2>/dev/null; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -ge "$MAX_ATTEMPTS" ]; then
    echo "Database did not become ready in time. Exiting."
    exit 1
  fi
  echo "Database not ready yet (attempt $ATTEMPTS/$MAX_ATTEMPTS). Retrying in 2s..."
  sleep 2
done
echo "Database is ready."

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting MentorConnect API server..."
# Workers count: rule of thumb (2 x CPU cores) + 1; overridable via GUNICORN_WORKERS
exec gunicorn app.main:app \
  --workers "${GUNICORN_WORKERS:-4}" \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 60 \
  --access-logfile - \
  --error-logfile -

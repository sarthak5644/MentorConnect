# MentorConnect Backend

A production-ready FastAPI backend for **MentorConnect** — a mentorship matchmaking
platform connecting students with verified mentors. Built with Clean Architecture
principles, full RBAC, JWT auth with refresh-token rotation, OTP (email + SMS),
image captcha, secure file uploads, audit logging, and a Super Admin
analytics/moderation suite.

---

## 1. Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | MySQL 8 |
| ORM | SQLAlchemy 2.0 (no raw SQL) |
| Migrations | Alembic |
| Validation | Pydantic v2 |
| Auth | JWT (access + refresh), bcrypt |
| Docs | Swagger UI (`/docs`) + ReDoc (`/redoc`) |
| Containerization | Docker + docker-compose |
| Rate limiting | slowapi |
| Image captcha | Pillow (hand-drawn distorted text, no external service) |
| Logging | loguru (rotating file + console sinks) |

---

## 2. Architecture (Clean Architecture)

```
app/
├── api/                    # Presentation layer - HTTP routing only, no business logic
│   ├── deps.py              # Shared FastAPI dependencies (auth, RBAC)
│   └── v1/
│       ├── router.py         # Aggregates all endpoint routers
│       └── endpoints/        # One file per resource (auth, mentors, bookings, ...)
├── schemas/                 # Pydantic request/response models (DTOs)
├── services/                 # Business logic layer - all use-cases live here
├── repositories/             # Data access layer - all SQLAlchemy queries live here
├── models/                   # SQLAlchemy ORM models (the persistence layer)
├── core/                     # Cross-cutting: config, security, logging, exceptions
├── middlewares/               # CSRF, rate limiting, security headers, exception handling
├── utils/                     # Sanitization, file validation helpers
└── db/                        # Engine/session setup, declarative base, seed script
alembic/                      # Database migrations
docs/                          # ER diagram (Mermaid + rendered PNG)
uploads/                       # Local file storage (profiles/documents/chat)
```

**Dependency direction:** `endpoints → services → repositories → models`.
Endpoints never touch SQLAlchemy directly; services never know about FastAPI/HTTP;
repositories never contain business rules. This keeps each layer independently
testable and swappable (e.g. repositories could move to a different ORM without
touching services or endpoints).

---

## 3. Database Schema

18 core tables from the spec, **plus `refresh_tokens`** (required for secure,
revocable JWT refresh flows — without it, a leaked refresh token could never be
invalidated short of rotating the signing secret for every user):

`roles`, `users`, `students`, `mentors`, `mentor_documents`,
`mentor_availability_slots`, `mentorship_requests`, `bookings`, `chats`,
`messages`, `notifications`, `ratings`, `complaints`, `otp_verifications`,
`captcha_sessions`, `audit_logs`, `categories`, `fields`, `mentor_fields`
(association table), `refresh_tokens`.

See **`docs/er-diagram.png`** for the rendered ER diagram, and
**`docs/er-diagram.mmd`** for the Mermaid source (renders on GitHub natively).

---

## 4. Getting Started

### 4.1 With Docker (recommended)

```bash
cp .env.example .env
# Edit .env: set real secrets for JWT_SECRET_KEY, JWT_REFRESH_SECRET_KEY,
# CSRF_SECRET_KEY, DB passwords, and SUPERADMIN_PASSWORD before going to production.

docker-compose up --build
```

This starts MySQL + the API. On first boot, the entrypoint script waits for
MySQL, runs `alembic upgrade head`, then starts Gunicorn+Uvicorn workers.
On application startup, `app/db/seed.py` automatically creates:
- The 3 RBAC roles (`super_admin`, `mentor`, `student`)
- A Super Admin account from `SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD`
- A small starter category/field taxonomy (Technology, Business, Design, ...)

Visit **http://localhost:8000/docs** for interactive Swagger documentation.

### 4.2 Local (without Docker)

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env   # point DB_HOST to your local MySQL instance

alembic upgrade head
python -m app.db.seed   # optional: seed.py also runs automatically on app startup

uvicorn app.main:app --reload
```

---

## 5. Authentication Flow

1. `GET /api/v1/auth/captcha` → returns `{session_id, image_base64}`.
2. User registers (`/auth/register/student` or `/auth/register/mentor`),
   submitting the captcha `session_id` + their typed answer.
3. `POST /api/v1/otp/email/send` and `/otp/mobile/send` → OTP codes sent
   (logged to console in dev if SMTP/SMS aren't configured — see
   `SMS_PROVIDER=console` default).
4. `POST /api/v1/otp/verify` for each channel → account flips to `ACTIVE`
   once both are verified.
5. `POST /api/v1/auth/login` (also captcha-gated) → returns `{access_token, refresh_token}`.
6. Use `Authorization: Bearer <access_token>` on all subsequent requests.
7. `POST /api/v1/auth/refresh` with the refresh token to rotate for a new pair
   (old refresh token is revoked on use — single-use rotation).
8. `POST /api/v1/auth/logout` (this session) or `/auth/logout-all` (every session).

Mentor accounts additionally require **Super Admin approval**
(`POST /api/v1/admin/mentors/{id}/approve`) before they appear in student search
results or can accept mentorship requests.

---

## 6. Role-Based Access Control

Three roles: `super_admin`, `mentor`, `student`. Enforced via the
`require_roles(...)` FastAPI dependency (`app/api/deps.py`), e.g.:

```python
current_user: User = Depends(require_roles(RoleName.MENTOR))
```

The entire `/admin/*` router is additionally gated at the router level via
`dependencies=[Depends(require_roles(RoleName.SUPER_ADMIN))]`.

---

## 7. Security Measures Implemented

| Requirement | Implementation |
|---|---|
| SQLAlchemy ORM only / no raw SQL | Every query uses the SQLAlchemy 2.0 `select()` construct — see `app/repositories/` |
| bcrypt password hashing | `passlib[bcrypt]`, configurable rounds (`app/core/security.py`) |
| JWT auth | Separate signing secrets for access vs. refresh tokens; `token_version` claim allows instant mass-invalidation |
| Refresh token security | Hashed (SHA-256) before DB storage; single-use rotation; per-session revocation |
| Rate limiting | `slowapi`, tighter limits on `/auth/login`, `/auth/register/*`, `/otp/*` |
| XSS protection | `utils/sanitizer.py` strips/escapes HTML on every free-text field (bios, messages, complaints); CSP + `X-XSS-Protection` response headers |
| SQL Injection protection | Inherent to parameterized ORM queries — no string-formatted SQL anywhere |
| CSRF protection | Double-submit-cookie pattern (`app/middlewares/csrf.py`) for any cookie-based session use |
| Secure file upload | Extension whitelist + **magic-byte verification** (rejects a renamed `.exe` claiming to be `.jpg`) + random server-generated filenames + size limits (`utils/file_validator.py`) |
| Input validation | Pydantic v2 schemas with regex/length/range constraints on every endpoint |
| Image captcha | Server-rendered distorted text (Pillow), hashed answer, single-use, time-limited |
| Audit logs | Immutable `audit_logs` table; every login, approval, rejection, block/unblock is recorded with actor, IP, and user agent |

---

## 8. Notable Design Decisions

- **Denormalized mentor rating stats** (`average_rating`, `total_ratings` on
  `mentors`) are recomputed on every new rating, trading a tiny bit of write
  cost for fast search/sort without aggregate queries on every search request.
- **Slot booking race protection**: booking a slot flips its status inside the
  same transaction as the `INSERT` into `bookings`; the `UNIQUE` constraint on
  `bookings.slot_id` plus `IntegrityError` handling guarantees two students
  can never double-book the same slot even under concurrent requests.
- **Chat auto-creation**: a `Chat` row is created automatically the moment a
  mentor accepts a `MentorshipRequest` — there's no separate "start chat" step.
- **OTP/Captcha answers are hashed**, never stored or logged in plaintext.
- **Generic error messages on `forgot-password`** regardless of whether the
  email exists, to prevent user-enumeration attacks.

---

## 9. API Documentation

Once running, full interactive documentation (every endpoint, request/response
schema, and the ability to try requests with a live Bearer token) is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Raw OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## 10. Project Conventions

- Every SQLAlchemy model lives in its own file under `app/models/`, all
  imported via `app/models/__init__.py` so Alembic's metadata is always complete.
- Every feature follows the same four-file pattern: `models/X.py` →
  `schemas/X.py` → `repositories/X_repository.py` → `services/X_service.py` →
  `api/v1/endpoints/X.py`.
- All list endpoints are paginated (`page`, `page_size` query params) and
  return a consistent `{success, message, total, page, page_size, total_pages, data}` envelope.
- All single-item responses return `{success, message, data}`.

---

## 11. Running Migrations

```bash
# Generate a new migration after changing models:
alembic revision --autogenerate -m "describe your change"

# Apply migrations:
alembic upgrade head

# Roll back one revision:
alembic downgrade -1
```

---

## 12. Default Super Admin Credentials

Set via `.env` (`SUPERADMIN_EMAIL` / `SUPERADMIN_PASSWORD`), seeded
automatically on first startup. **Change this password immediately after your
first login in any non-local environment.**

"""
tests/test_auth.py
---------------------
Smoke tests for the authentication flow: captcha generation, student/mentor
registration, and login. Uses the in-memory SQLite fixtures from conftest.py.
"""


def _get_captcha_and_solve(client, db_session):
    """
    Helper: creates a captcha record directly via the service/repo so the test
    knows the plaintext answer (in production the answer is never recoverable
    once issued - it's one-way hashed immediately).
    """
    from app.services.captcha_service import CaptchaService
    from app.core.config import settings
    from app.core.security import hash_token
    from datetime import datetime, timedelta
    import uuid

    service = CaptchaService(db_session)
    text = "TEST12"
    session_id = uuid.uuid4().hex
    service.repo.create({
        "session_id": session_id,
        "hashed_answer": hash_token(text.upper()),
        "is_used": False,
        "expires_at": datetime.utcnow() + timedelta(minutes=settings.CAPTCHA_EXPIRE_MINUTES),
    })
    return session_id, text


def test_captcha_endpoint_returns_image(client):
    response = client.get("/api/v1/auth/captcha")
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "session_id" in body["data"]
    assert "image_base64" in body["data"]


def test_student_registration_success(client, db_session):
    session_id, answer = _get_captcha_and_solve(client, db_session)

    payload = {
        "full_name": "Test Student",
        "email": "student1@example.com",
        "mobile_number": "+919876543210",
        "password": "StrongPass1!",
        "captcha_session_id": session_id,
        "captcha_answer": answer,
        "institution_name": "Test University",
    }
    response = client.post("/api/v1/auth/register/student", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["data"]["email"] == "student1@example.com"
    assert body["data"]["role"]["name"] == "student"


def test_duplicate_email_registration_fails(client, db_session):
    session_id, answer = _get_captcha_and_solve(client, db_session)
    payload = {
        "full_name": "Test Student",
        "email": "dupe@example.com",
        "mobile_number": "+919876543211",
        "password": "StrongPass1!",
        "captcha_session_id": session_id,
        "captcha_answer": answer,
    }
    first = client.post("/api/v1/auth/register/student", json=payload)
    assert first.status_code == 201

    session_id2, answer2 = _get_captcha_and_solve(client, db_session)
    payload["captcha_session_id"] = session_id2
    payload["captcha_answer"] = answer2
    payload["mobile_number"] = "+919876543212"

    second = client.post("/api/v1/auth/register/student", json=payload)
    assert second.status_code == 409
    assert second.json()["error_code"] == "CONFLICT"


def test_weak_password_rejected(client, db_session):
    session_id, answer = _get_captcha_and_solve(client, db_session)
    payload = {
        "full_name": "Weak Pass",
        "email": "weak@example.com",
        "mobile_number": "+919876543213",
        "password": "weak",
        "captcha_session_id": session_id,
        "captcha_answer": answer,
    }
    response = client.post("/api/v1/auth/register/student", json=payload)
    assert response.status_code == 422

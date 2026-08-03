"""
app/api/v1/router.py
------------------------
Aggregates all v1 endpoint routers into a single APIRouter, mounted in
main.py under the configured API_V1_PREFIX (default /api/v1).
"""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, otp, students, mentors, mentorship_requests, bookings,
    chats, ratings, complaints, notifications, categories, admin,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(otp.router)
api_router.include_router(students.router)
api_router.include_router(mentors.router)
api_router.include_router(mentorship_requests.router)
api_router.include_router(bookings.router)
api_router.include_router(chats.router)
api_router.include_router(ratings.router)
api_router.include_router(complaints.router)
api_router.include_router(notifications.router)
api_router.include_router(categories.router)
api_router.include_router(admin.router)

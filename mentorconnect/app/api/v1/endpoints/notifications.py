"""
app/api/v1/endpoints/notifications.py
--------------------------------------------
Endpoints for in-app notifications: list mine, unread count, mark read.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.notification_service import NotificationService
from app.schemas.common import ApiResponse
from app.schemas.notification import NotificationOut, NotificationMarkReadRequest

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=ApiResponse[List[NotificationOut]], summary="List my notifications")
def list_notifications(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    notifications = service.list_for_user(current_user.id, (page - 1) * page_size, page_size)
    return ApiResponse(data=notifications)


@router.get("/unread-count", response_model=ApiResponse[dict], summary="Get my unread notification count")
def unread_count(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = NotificationService(db)
    count = service.unread_count(current_user.id)
    return ApiResponse(data={"unread_count": count})


@router.post("/mark-read", response_model=ApiResponse[None], summary="Mark notifications as read")
def mark_read(
    payload: NotificationMarkReadRequest, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    service.mark_read(current_user.id, payload.notification_ids)
    return ApiResponse(message="Notifications marked as read.")

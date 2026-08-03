"""
app/api/v1/endpoints/bookings.py
------------------------------------
Endpoints for students booking mentor slots and managing booking lifecycle.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles, get_current_user
from app.models.enums import RoleName, BookingStatus
from app.models.user import User
from app.services.booking_service import BookingService
from app.services.student_service import StudentService
from app.services.mentor_service import MentorService
from app.schemas.common import ApiResponse
from app.schemas.booking import BookingCreateRequest, BookingCancelRequest, BookingOut

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/", response_model=ApiResponse[BookingOut], summary="Book a mentor's availability slot")
def create_booking(
    payload: BookingCreateRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    student = StudentService(db).get_by_user(current_user)
    service = BookingService(db)
    booking = service.create_booking(student, payload)
    return ApiResponse(message="Slot booked successfully.", data=booking)


@router.get("/my", response_model=ApiResponse[List[BookingOut]], summary="List my bookings (student)")
def list_my_bookings(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    student = StudentService(db).get_by_user(current_user)
    service = BookingService(db)
    bookings = service.list_for_student(student.id, (page - 1) * page_size, page_size)
    return ApiResponse(data=bookings)


@router.get(
    "/mentor", response_model=ApiResponse[List[BookingOut]],
    summary="List bookings for my mentor sessions (mentor)",
)
def list_mentor_bookings(
    status_filter: Optional[BookingStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    mentor = MentorService(db).get_mentor_by_user(current_user)
    service = BookingService(db)
    bookings = service.list_for_mentor(mentor.id, status_filter, (page - 1) * page_size, page_size)
    return ApiResponse(data=bookings)


@router.post("/{booking_id}/cancel", response_model=ApiResponse[BookingOut], summary="Cancel a booking")
def cancel_booking(
    booking_id: int, payload: BookingCancelRequest, db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = BookingService(db)
    booking = service.cancel_booking(current_user.id, booking_id, payload.cancellation_reason)
    return ApiResponse(message="Booking cancelled successfully.", data=booking)


@router.post(
    "/{booking_id}/complete", response_model=ApiResponse[BookingOut],
    summary="Mark a booking as completed (mentor)",
)
def complete_booking(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = BookingService(db)
    booking = service.mark_completed(current_user.id, booking_id)
    return ApiResponse(message="Booking marked as completed.", data=booking)


@router.post(
    "/{booking_id}/no-show", response_model=ApiResponse[BookingOut],
    summary="Mark a booking as no-show (mentor)",
)
def mark_no_show(
    booking_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = BookingService(db)
    booking = service.mark_no_show(current_user.id, booking_id)
    return ApiResponse(message="Booking marked as no-show.", data=booking)

"""
app/api/v1/endpoints/mentorship_requests.py
-------------------------------------------------
Endpoints for students sending mentorship requests, and mentors
accepting/rejecting/listing them.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import RoleName, MentorshipRequestStatus
from app.models.user import User
from app.services.mentorship_request_service import MentorshipRequestService
from app.services.student_service import StudentService
from app.services.mentor_service import MentorService
from app.schemas.common import ApiResponse
from app.schemas.mentorship_request import (
    MentorshipRequestCreate, MentorshipRequestRespond, MentorshipRequestOut,
)

router = APIRouter(prefix="/mentorship-requests", tags=["Mentorship Requests"])


@router.post("/", response_model=ApiResponse[MentorshipRequestOut], summary="Send a mentorship request to a mentor")
def create_request(
    payload: MentorshipRequestCreate, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    student = StudentService(db).get_by_user(current_user)
    service = MentorshipRequestService(db)
    request = service.create_request(student, payload)
    return ApiResponse(message="Mentorship request sent successfully.", data=request)


@router.get(
    "/sent", response_model=ApiResponse[List[MentorshipRequestOut]],
    summary="List requests I've sent (student)",
)
def list_sent_requests(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    student = StudentService(db).get_by_user(current_user)
    service = MentorshipRequestService(db)
    requests = service.list_for_student(student.id, (page - 1) * page_size, page_size)
    return ApiResponse(data=requests)


@router.get(
    "/received", response_model=ApiResponse[List[MentorshipRequestOut]],
    summary="List requests I've received (mentor)",
)
def list_received_requests(
    status_filter: Optional[MentorshipRequestStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    mentor = MentorService(db).get_mentor_by_user(current_user)
    service = MentorshipRequestService(db)
    requests = service.list_for_mentor(mentor.id, status_filter, (page - 1) * page_size, page_size)
    return ApiResponse(data=requests)


@router.post(
    "/{request_id}/respond", response_model=ApiResponse[MentorshipRequestOut],
    summary="Accept or reject a mentorship request (mentor)",
)
def respond_to_request(
    request_id: int, payload: MentorshipRequestRespond, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    mentor = MentorService(db).get_mentor_by_user(current_user)
    service = MentorshipRequestService(db)
    request = service.respond_to_request(mentor, request_id, payload)
    return ApiResponse(message=f"Request {payload.status.value} successfully.", data=request)


@router.post(
    "/{request_id}/cancel", response_model=ApiResponse[MentorshipRequestOut],
    summary="Cancel a pending mentorship request (student)",
)
def cancel_request(
    request_id: int, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    student = StudentService(db).get_by_user(current_user)
    service = MentorshipRequestService(db)
    request = service.cancel_request(student, request_id)
    return ApiResponse(message="Request cancelled successfully.", data=request)

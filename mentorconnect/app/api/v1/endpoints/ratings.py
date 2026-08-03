"""
app/api/v1/endpoints/ratings.py
------------------------------------
Endpoints for students rating mentors after a completed booking.
"""

from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles, get_current_user
from app.models.enums import RoleName
from app.models.user import User
from app.services.rating_service import RatingService
from app.services.student_service import StudentService
from app.schemas.common import ApiResponse
from app.schemas.rating import RatingCreateRequest, RatingOut

router = APIRouter(prefix="/ratings", tags=["Ratings & Reviews"])


@router.post("/", response_model=ApiResponse[RatingOut], summary="Rate a mentor after a completed booking")
def create_rating(
    payload: RatingCreateRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    student = StudentService(db).get_by_user(current_user)
    service = RatingService(db)
    rating = service.create_rating(student, payload)
    return ApiResponse(message="Thank you for your feedback!", data=rating)


@router.get(
    "/mentor/{mentor_id}", response_model=ApiResponse[List[RatingOut]],
    summary="List ratings for a mentor",
)
def list_mentor_ratings(
    mentor_id: int, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user),
):
    service = RatingService(db)
    ratings = service.list_for_mentor(mentor_id, (page - 1) * page_size, page_size)
    return ApiResponse(data=ratings)

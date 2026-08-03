"""
app/api/v1/endpoints/mentors.py
-----------------------------------
Mentor profile management endpoints (self-service) plus the public
student-facing mentor search/discovery endpoint.
"""

import math
from typing import Optional, List
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles, get_current_user
from app.models.enums import RoleName, SlotStatus
from app.models.user import User
from app.services.mentor_service import MentorService
from app.schemas.common import ApiResponse, PaginatedResponse
from app.schemas.mentor import (
    MentorProfileUpdate, MentorQualificationsUpdate, MentorAchievementsUpdate, MentorExpertiseUpdate,
    MentorProfileResponse, MentorOut, MentorPublicCard, MentorSearchFilters,
)
from app.schemas.mentor_document import MentorDocumentOut
from app.schemas.availability_slot import SlotCreateRequest, BulkSlotCreateRequest, SlotOut
from app.schemas.user import UserOut

router = APIRouter(prefix="/mentors", tags=["Mentors"])


# ----------------------------------------------------------------------
# Self-service profile management (Mentor role only)
# ----------------------------------------------------------------------
@router.get("/me", response_model=ApiResponse[MentorProfileResponse], summary="Get my mentor profile")
def get_my_profile(db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.MENTOR))):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    return ApiResponse(data=MentorProfileResponse(
        user=UserOut.model_validate(current_user), profile=MentorOut.model_validate(mentor),
    ))


@router.put("/me", response_model=ApiResponse[MentorOut], summary="Update my mentor profile")
def update_my_profile(
    payload: MentorProfileUpdate, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    updated = service.update_profile(mentor, payload)
    return ApiResponse(message="Profile updated successfully.", data=MentorOut.model_validate(updated))


@router.put("/me/qualifications", response_model=ApiResponse[MentorOut], summary="Update my qualifications")
def update_qualifications(
    payload: MentorQualificationsUpdate, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    updated = service.update_qualifications(mentor, payload)
    return ApiResponse(message="Qualifications updated successfully.", data=MentorOut.model_validate(updated))


@router.put("/me/achievements", response_model=ApiResponse[MentorOut], summary="Update my achievements")
def update_achievements(
    payload: MentorAchievementsUpdate, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    updated = service.update_achievements(mentor, payload)
    return ApiResponse(message="Achievements updated successfully.", data=MentorOut.model_validate(updated))


@router.put("/me/expertise", response_model=ApiResponse[MentorOut], summary="Update my fields of expertise")
def update_expertise(
    payload: MentorExpertiseUpdate, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    updated = service.update_expertise(mentor, payload.field_ids)
    return ApiResponse(message="Expertise updated successfully.", data=MentorOut.model_validate(updated))


@router.post("/me/profile-image", response_model=ApiResponse[dict], summary="Upload my profile image")
async def upload_profile_image(
    file: UploadFile = File(...), db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = MentorService(db)
    relative_path = await service.upload_profile_image(current_user, file)
    return ApiResponse(message="Profile image uploaded successfully.", data={"profile_image_url": relative_path})


# ----------------------------------------------------------------------
# Mentor documents (upload for verification)
# ----------------------------------------------------------------------
@router.post(
    "/me/documents", response_model=ApiResponse[MentorDocumentOut],
    summary="Upload a verification document (ID proof, degree certificate, etc.)",
)
async def upload_document(
    document_type: str, file: UploadFile = File(...), db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    document = await service.upload_document(mentor, document_type, file)
    return ApiResponse(message="Document uploaded successfully. Pending admin review.", data=document)


@router.get(
    "/me/documents", response_model=ApiResponse[List[MentorDocumentOut]],
    summary="List my uploaded documents",
)
def list_my_documents(db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.MENTOR))):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    documents = service.list_documents(mentor.id)
    return ApiResponse(data=documents)


# ----------------------------------------------------------------------
# Availability slots
# ----------------------------------------------------------------------
@router.post("/me/slots", response_model=ApiResponse[SlotOut], summary="Create a new availability slot")
def create_slot(
    payload: SlotCreateRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    slot = service.create_slot(mentor, payload)
    return ApiResponse(message="Slot created successfully.", data=slot)


@router.post(
    "/me/slots/bulk", response_model=ApiResponse[List[SlotOut]],
    summary="Create multiple availability slots at once",
)
def create_bulk_slots(
    payload: BulkSlotCreateRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    slots = service.create_bulk_slots(mentor, payload.slots)
    return ApiResponse(message=f"{len(slots)} slots created successfully.", data=slots)


@router.get("/me/slots", response_model=ApiResponse[List[SlotOut]], summary="List my availability slots")
def list_my_slots(
    status_filter: Optional[SlotStatus] = Query(None, alias="status"),
    upcoming_only: bool = Query(True),
    db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    slots = service.list_slots(mentor.id, status=status_filter, upcoming_only=upcoming_only)
    return ApiResponse(data=slots)


@router.delete("/me/slots/{slot_id}", response_model=ApiResponse[None], summary="Delete an availability slot")
def delete_slot(
    slot_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.MENTOR)),
):
    service = MentorService(db)
    mentor = service.get_mentor_by_user(current_user)
    service.delete_slot(mentor, slot_id)
    return ApiResponse(message="Slot deleted successfully.")


# ----------------------------------------------------------------------
# Public: Search / Discovery (any authenticated user, typically students)
# ----------------------------------------------------------------------
@router.get("/search", response_model=PaginatedResponse[MentorPublicCard], summary="Search and filter mentors")
def search_mentors(
    keyword: Optional[str] = None,
    field_id: Optional[int] = None,
    category_id: Optional[int] = None,
    min_rating: Optional[float] = None,
    max_hourly_rate: Optional[float] = None,
    min_experience: Optional[int] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,
    is_accepting_requests: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = MentorSearchFilters(
        keyword=keyword, field_id=field_id, category_id=category_id, min_rating=min_rating,
        max_hourly_rate=max_hourly_rate, min_experience=min_experience, city=city, country=country,
        is_accepting_requests=is_accepting_requests,
    )
    service = MentorService(db)
    skip = (page - 1) * page_size
    results, total = service.search_mentors(filters, skip, page_size)
    return PaginatedResponse(
        total=total, page=page, page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
        data=[MentorPublicCard.model_validate(m) for m in results],
    )


@router.get("/{mentor_id}", response_model=ApiResponse[MentorOut], summary="Get a mentor's public profile by ID")
def get_mentor_profile(mentor_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = MentorService(db)
    mentor = service.get_mentor_or_404(mentor_id)
    return ApiResponse(data=MentorOut.model_validate(mentor))

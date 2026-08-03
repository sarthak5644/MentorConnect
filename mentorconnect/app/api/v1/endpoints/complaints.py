"""
app/api/v1/endpoints/complaints.py
---------------------------------------
Endpoints for students filing complaints and admins resolving them.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import RoleName, ComplaintStatus
from app.models.user import User
from app.services.complaint_service import ComplaintService
from app.services.student_service import StudentService
from app.schemas.common import ApiResponse
from app.schemas.complaint import ComplaintCreateRequest, ComplaintResolveRequest, ComplaintOut

router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("/", response_model=ApiResponse[ComplaintOut], summary="File a complaint")
def create_complaint(
    payload: ComplaintCreateRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    student = StudentService(db).get_by_user(current_user)
    service = ComplaintService(db)
    complaint = service.create_complaint(student, payload)
    return ApiResponse(message="Complaint filed successfully. Our team will review it shortly.", data=complaint)


@router.get("/my", response_model=ApiResponse[List[ComplaintOut]], summary="List my filed complaints")
def list_my_complaints(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    student = StudentService(db).get_by_user(current_user)
    service = ComplaintService(db)
    complaints = service.list_for_student(student.id, (page - 1) * page_size, page_size)
    return ApiResponse(data=complaints)


@router.get("/", response_model=ApiResponse[List[ComplaintOut]], summary="List all complaints (admin)")
def list_all_complaints(
    status_filter: Optional[ComplaintStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN)),
):
    service = ComplaintService(db)
    complaints = service.list_all(status_filter, (page - 1) * page_size, page_size)
    return ApiResponse(data=complaints)


@router.post(
    "/{complaint_id}/resolve", response_model=ApiResponse[ComplaintOut],
    summary="Resolve or dismiss a complaint (admin)",
)
def resolve_complaint(
    complaint_id: int, payload: ComplaintResolveRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN)),
):
    service = ComplaintService(db)
    complaint = service.resolve_complaint(current_user, complaint_id, payload)
    return ApiResponse(message=f"Complaint {payload.status.value}.", data=complaint)

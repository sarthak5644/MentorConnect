"""
app/api/v1/endpoints/admin.py
---------------------------------
Super Admin endpoints: mentor approval workflow, document review, dashboard
KPIs, analytics/reports, user blocking, and audit log access.
All endpoints in this router require the SUPER_ADMIN role.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import RoleName, UserStatus, AuditAction
from app.models.user import User
from app.services.mentor_service import MentorService
from app.services.admin_service import AdminService
from app.repositories.audit_log_repository import AuditLogRepository
from app.schemas.common import ApiResponse
from app.schemas.mentor import MentorApprovalRequest, MentorRejectionRequest, MentorOut
from app.schemas.mentor_document import MentorDocumentReviewRequest, MentorDocumentOut
from app.schemas.admin import BlockUserRequest
from app.schemas.user import UserOut
from app.schemas.dashboard import DashboardSummary, AnalyticsReport
from app.schemas.audit_log import AuditLogOut

router = APIRouter(
    prefix="/admin", tags=["Super Admin"],
    dependencies=[Depends(require_roles(RoleName.SUPER_ADMIN))],
)


# ----------------------------------------------------------------------
# Mentor Approval Workflow
# ----------------------------------------------------------------------
@router.get(
    "/mentors/pending", response_model=ApiResponse[List[MentorOut]],
    summary="List mentors pending approval",
)
def list_pending_mentors(
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db),
):
    service = MentorService(db)
    mentors = service.list_pending_approval((page - 1) * page_size, page_size)
    return ApiResponse(data=mentors)


@router.post(
    "/mentors/{mentor_id}/approve", response_model=ApiResponse[MentorOut],
    summary="Approve a mentor application",
)
async def approve_mentor(
    mentor_id: int, payload: MentorApprovalRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN)),
):
    service = MentorService(db)
    mentor = await service.approve_mentor(mentor_id, current_user, payload.notes)
    return ApiResponse(message="Mentor approved successfully.", data=mentor)


@router.post(
    "/mentors/{mentor_id}/reject", response_model=ApiResponse[MentorOut],
    summary="Reject a mentor application",
)
async def reject_mentor(
    mentor_id: int, payload: MentorRejectionRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN)),
):
    service = MentorService(db)
    mentor = await service.reject_mentor(mentor_id, current_user, payload.rejection_reason)
    return ApiResponse(message="Mentor application rejected.", data=mentor)


@router.post(
    "/documents/{document_id}/review", response_model=ApiResponse[MentorDocumentOut],
    summary="Review (verify/reject) a mentor's uploaded document",
)
def review_document(
    document_id: int, payload: MentorDocumentReviewRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN)),
):
    service = MentorService(db)
    document = service.review_document(document_id, current_user, payload.status, payload.rejection_reason)
    return ApiResponse(message="Document reviewed successfully.", data=document)


# ----------------------------------------------------------------------
# User Management
# ----------------------------------------------------------------------
@router.get(
    "/users", response_model=ApiResponse[List[UserOut]],
    summary="List users, optionally filtered by status",
)
def list_users(
    status_filter: Optional[UserStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db),
):
    service = AdminService(db)
    users = service.list_users(status_filter, (page - 1) * page_size, page_size)
    return ApiResponse(data=users)


@router.post("/users/{user_id}/block", response_model=ApiResponse[UserOut], summary="Block a user account")
def block_user(
    user_id: int, payload: BlockUserRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN)),
):
    service = AdminService(db)
    user = service.block_user(current_user, user_id, payload.reason)
    return ApiResponse(message="User blocked successfully.", data=user)


@router.post("/users/{user_id}/unblock", response_model=ApiResponse[UserOut], summary="Unblock a user account")
def unblock_user(
    user_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN)),
):
    service = AdminService(db)
    user = service.unblock_user(current_user, user_id)
    return ApiResponse(message="User unblocked successfully.", data=user)


# ----------------------------------------------------------------------
# Dashboard / Analytics / Reports
# ----------------------------------------------------------------------
@router.get("/dashboard", response_model=ApiResponse[DashboardSummary], summary="Get dashboard KPI summary")
def get_dashboard(db: Session = Depends(get_db)):
    service = AdminService(db)
    summary = service.get_dashboard_summary()
    return ApiResponse(data=summary)


@router.get("/analytics", response_model=ApiResponse[AnalyticsReport], summary="Get analytics/report data")
def get_analytics(db: Session = Depends(get_db)):
    service = AdminService(db)
    report = service.get_analytics_report()
    return ApiResponse(data=report)


# ----------------------------------------------------------------------
# Audit Logs
# ----------------------------------------------------------------------
@router.get("/audit-logs", response_model=ApiResponse[List[AuditLogOut]], summary="View the audit trail")
def list_audit_logs(
    action: Optional[AuditAction] = None, entity_type: Optional[str] = None,
    page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200), db: Session = Depends(get_db),
):
    repo = AuditLogRepository(db)
    logs = repo.list_all(action, entity_type, (page - 1) * page_size, page_size)
    return ApiResponse(data=logs)

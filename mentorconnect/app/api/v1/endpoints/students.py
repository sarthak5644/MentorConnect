"""
app/api/v1/endpoints/students.py
------------------------------------
Student profile endpoints (self-service: view/update own profile).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles
from app.models.enums import RoleName
from app.models.user import User
from app.services.student_service import StudentService
from app.schemas.common import ApiResponse
from app.schemas.student import StudentProfileUpdate, StudentProfileResponse, StudentOut
from app.schemas.user import UserOut

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("/me", response_model=ApiResponse[StudentProfileResponse], summary="Get my student profile")
def get_my_profile(
    db: Session = Depends(get_db), current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    service = StudentService(db)
    student = service.get_by_user(current_user)
    return ApiResponse(data=StudentProfileResponse(
        user=UserOut.model_validate(current_user), profile=StudentOut.model_validate(student),
    ))


@router.put("/me", response_model=ApiResponse[StudentOut], summary="Update my student profile")
def update_my_profile(
    payload: StudentProfileUpdate, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.STUDENT)),
):
    service = StudentService(db)
    student = service.get_by_user(current_user)
    updated = service.update_profile(student, payload)
    return ApiResponse(message="Profile updated successfully.", data=StudentOut.model_validate(updated))

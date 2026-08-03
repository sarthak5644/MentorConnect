"""
app/api/v1/endpoints/categories.py
---------------------------------------
Endpoints for the Category/Field taxonomy: public read access, admin-only writes.
"""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.api.deps import require_roles, get_current_user
from app.models.enums import RoleName
from app.models.user import User
from app.services.category_service import CategoryService
from app.schemas.common import ApiResponse
from app.schemas.category import CategoryCreateRequest, FieldCreateRequest, CategoryOut, FieldOut

router = APIRouter(prefix="/categories", tags=["Categories & Fields"])


@router.get(
    "/", response_model=ApiResponse[List[CategoryOut]],
    summary="List all active categories and their fields",
)
def list_categories(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CategoryService(db)
    categories = service.list_categories()
    return ApiResponse(data=categories)


@router.post("/", response_model=ApiResponse[CategoryOut], summary="Create a new category (admin)")
def create_category(
    payload: CategoryCreateRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN)),
):
    service = CategoryService(db)
    category = service.create_category(payload)
    return ApiResponse(message="Category created successfully.", data=category)


@router.post(
    "/fields", response_model=ApiResponse[FieldOut],
    summary="Create a new field under a category (admin)",
)
def create_field(
    payload: FieldCreateRequest, db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(RoleName.SUPER_ADMIN)),
):
    service = CategoryService(db)
    field = service.create_field(payload)
    return ApiResponse(message="Field created successfully.", data=field)


@router.get(
    "/{category_id}/fields", response_model=ApiResponse[List[FieldOut]],
    summary="List fields under a specific category",
)
def list_fields(category_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    service = CategoryService(db)
    fields = service.list_fields_by_category(category_id)
    return ApiResponse(data=fields)

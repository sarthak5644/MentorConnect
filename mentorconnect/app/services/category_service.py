"""
app/services/category_service.py
------------------------------------
Business logic for managing the Category/Field taxonomy used to classify
mentor expertise (admin-managed, but read by everyone for search filters).
"""

from typing import List
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.category import Category, Field as FieldModel
from app.repositories.category_repository import CategoryRepository, FieldRepository
from app.schemas.category import CategoryCreateRequest, FieldCreateRequest


class CategoryService:
    def __init__(self, db: Session):
        self.db = db
        self.category_repo = CategoryRepository(db)
        self.field_repo = FieldRepository(db)

    def list_categories(self) -> List[Category]:
        return self.category_repo.list_active()

    def create_category(self, payload: CategoryCreateRequest) -> Category:
        existing = self.category_repo.get_by_name(payload.name)
        if existing is not None:
            raise ConflictException("A category with this name already exists.")
        return self.category_repo.create({
            "name": payload.name,
            "description": payload.description,
            "is_active": True,
        })

    def create_field(self, payload: FieldCreateRequest) -> FieldModel:
        category = self.category_repo.get(payload.category_id)
        if category is None:
            raise NotFoundException("Category not found.")
        return self.field_repo.create({
            "category_id": payload.category_id,
            "name": payload.name,
            "is_active": True,
        })

    def list_fields_by_category(self, category_id: int) -> List[FieldModel]:
        return self.field_repo.list_by_category(category_id)

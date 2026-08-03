"""
app/repositories/category_repository.py
-----------------------------------------------
Data access methods for Category and Field taxonomy entities.
"""

from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.category import Category, Field as FieldModel
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db: Session):
        super().__init__(Category, db)

    def list_active(self) -> List[Category]:
        stmt = (
            select(Category)
            .where(Category.is_active == True)  # noqa: E712
            .options(joinedload(Category.fields))
        )
        return list(self.db.execute(stmt).unique().scalars().all())

    def get_by_name(self, name: str) -> Optional[Category]:
        stmt = select(Category).where(Category.name == name)
        return self.db.execute(stmt).scalar_one_or_none()


class FieldRepository(BaseRepository[FieldModel]):
    def __init__(self, db: Session):
        super().__init__(FieldModel, db)

    def list_by_category(self, category_id: int) -> List[FieldModel]:
        stmt = select(FieldModel).where(FieldModel.category_id == category_id, FieldModel.is_active == True)  # noqa: E712
        return list(self.db.execute(stmt).scalars().all())

    def get_many_by_ids(self, field_ids: List[int]) -> List[FieldModel]:
        if not field_ids:
            return []
        stmt = select(FieldModel).where(FieldModel.id.in_(field_ids))
        return list(self.db.execute(stmt).scalars().all())

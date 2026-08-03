"""
app/repositories/student_repository.py
-------------------------------------------
Data access methods specific to the Student entity.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.student import Student
from app.repositories.base import BaseRepository


class StudentRepository(BaseRepository[Student]):
    def __init__(self, db: Session):
        super().__init__(Student, db)

    def get_by_user_id(self, user_id: int) -> Optional[Student]:
        stmt = select(Student).where(Student.user_id == user_id)
        return self.db.execute(stmt).scalar_one_or_none()

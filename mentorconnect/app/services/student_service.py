"""
app/services/student_service.py
-----------------------------------
Business logic for student profile management.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.student import Student
from app.models.user import User
from app.repositories.student_repository import StudentRepository
from app.utils.sanitizer import sanitize_text
from app.schemas.student import StudentProfileUpdate


class StudentService:
    def __init__(self, db: Session):
        self.db = db
        self.student_repo = StudentRepository(db)

    def get_by_user(self, user: User) -> Student:
        student = self.student_repo.get_by_user_id(user.id)
        if student is None:
            raise NotFoundException("Student profile not found for this account.")
        return student

    def update_profile(self, student: Student, payload: StudentProfileUpdate) -> Student:
        data = payload.model_dump(exclude_unset=True)
        if "bio" in data:
            data["bio"] = sanitize_text(data["bio"])
        if "interests" in data:
            data["interests"] = sanitize_text(data["interests"])

        for field, value in data.items():
            setattr(student, field, value)
        self.db.add(student)
        self.db.commit()
        self.db.refresh(student)
        return student

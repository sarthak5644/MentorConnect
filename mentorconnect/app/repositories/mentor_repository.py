"""
app/repositories/mentor_repository.py
-------------------------------------------
Data access methods specific to the Mentor entity, including the
search/filter query used by the student-facing mentor discovery endpoint.
"""

from typing import Optional, List, Tuple
from sqlalchemy import select, func, or_
from sqlalchemy.orm import Session, joinedload

from app.models.mentor import Mentor
from app.models.user import User
from app.models.category import Field as FieldModel, mentor_fields
from app.models.enums import MentorApprovalStatus, UserStatus
from app.repositories.base import BaseRepository
from app.schemas.mentor import MentorSearchFilters


class MentorRepository(BaseRepository[Mentor]):
    def __init__(self, db: Session):
        super().__init__(Mentor, db)

    def get_by_user_id(self, user_id: int) -> Optional[Mentor]:
        stmt = (
            select(Mentor)
            .where(Mentor.user_id == user_id)
            .options(joinedload(Mentor.expertise_fields))
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def get_with_relations(self, mentor_id: int) -> Optional[Mentor]:
        stmt = (
            select(Mentor)
            .where(Mentor.id == mentor_id)
            .options(joinedload(Mentor.expertise_fields), joinedload(Mentor.user))
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def list_pending_approval(self, skip: int = 0, limit: int = 20) -> List[Mentor]:
        stmt = (
            select(Mentor)
            .where(Mentor.approval_status == MentorApprovalStatus.PENDING)
            .offset(skip).limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def count_by_approval_status(self, status: MentorApprovalStatus) -> int:
        stmt = select(func.count()).select_from(Mentor).where(Mentor.approval_status == status)
        return self.db.execute(stmt).scalar_one()

    def search(self, filters: MentorSearchFilters, skip: int = 0, limit: int = 20) -> Tuple[List[Mentor], int]:
        """
        Search/filter approved & active mentors based on multiple optional criteria.
        Returns (results, total_count) for pagination.
        Only joins User to filter on account status and keyword search across name/headline/bio.
        """
        base_stmt = (
            select(Mentor)
            .join(User, Mentor.user_id == User.id)
            .where(
                Mentor.approval_status == MentorApprovalStatus.APPROVED,
                User.status == UserStatus.ACTIVE,
            )
            .options(joinedload(Mentor.expertise_fields))
        )

        if filters.keyword:
            like_pattern = f"%{filters.keyword.strip()}%"
            base_stmt = base_stmt.where(
                or_(
                    User.full_name.ilike(like_pattern),
                    Mentor.headline.ilike(like_pattern),
                    Mentor.bio.ilike(like_pattern),
                )
            )

        if filters.field_id is not None:
            base_stmt = base_stmt.join(mentor_fields, mentor_fields.c.mentor_id == Mentor.id).where(
                mentor_fields.c.field_id == filters.field_id
            )

        if filters.category_id is not None:
            base_stmt = base_stmt.join(
                mentor_fields, mentor_fields.c.mentor_id == Mentor.id, isouter=False
            ).join(FieldModel, FieldModel.id == mentor_fields.c.field_id).where(
                FieldModel.category_id == filters.category_id
            )

        if filters.min_rating is not None:
            base_stmt = base_stmt.where(Mentor.average_rating >= filters.min_rating)

        if filters.max_hourly_rate is not None:
            base_stmt = base_stmt.where(Mentor.hourly_rate <= filters.max_hourly_rate)

        if filters.min_experience is not None:
            base_stmt = base_stmt.where(Mentor.years_of_experience >= filters.min_experience)

        if filters.city:
            base_stmt = base_stmt.where(Mentor.city.ilike(f"%{filters.city.strip()}%"))

        if filters.country:
            base_stmt = base_stmt.where(Mentor.country.ilike(f"%{filters.country.strip()}%"))

        if filters.is_accepting_requests is not None:
            base_stmt = base_stmt.where(Mentor.is_accepting_requests == filters.is_accepting_requests)

        # Count total matches (distinct, since joins on mentor_fields can duplicate rows)
        count_stmt = select(func.count(func.distinct(Mentor.id))).select_from(base_stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        results_stmt = (
            base_stmt.distinct()
            .order_by(Mentor.average_rating.desc(), Mentor.total_ratings.desc())
            .offset(skip)
            .limit(limit)
        )
        results = list(self.db.execute(results_stmt).unique().scalars().all())
        return results, total

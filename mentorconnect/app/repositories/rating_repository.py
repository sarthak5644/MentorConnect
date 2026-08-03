"""
app/repositories/rating_repository.py
--------------------------------------------
Data access methods for mentor ratings/reviews.
"""

from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.rating import Rating
from app.repositories.base import BaseRepository


class RatingRepository(BaseRepository[Rating]):
    def __init__(self, db: Session):
        super().__init__(Rating, db)

    def get_by_booking_id(self, booking_id: int) -> Optional[Rating]:
        stmt = select(Rating).where(Rating.booking_id == booking_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def list_by_mentor(self, mentor_id: int, skip: int = 0, limit: int = 20) -> List[Rating]:
        stmt = (
            select(Rating)
            .where(Rating.mentor_id == mentor_id)
            .order_by(Rating.created_at.desc())
            .offset(skip).limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_mentor_aggregate(self, mentor_id: int) -> tuple[float, int]:
        """Returns (average_score, total_count) for a mentor's ratings."""
        stmt = select(func.avg(Rating.score), func.count(Rating.id)).where(Rating.mentor_id == mentor_id)
        avg_score, total = self.db.execute(stmt).one()
        return (float(avg_score) if avg_score is not None else 0.0, total or 0)

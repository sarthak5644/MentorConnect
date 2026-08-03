"""
app/services/rating_service.py
----------------------------------
Business logic for students rating mentors after a completed booking.
Updates the mentor's denormalized average_rating/total_ratings on each new rating.
"""

from typing import List
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.models.enums import BookingStatus, NotificationType
from app.models.rating import Rating
from app.models.student import Student
from app.repositories.rating_repository import RatingRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.mentor_repository import MentorRepository
from app.services.notification_service import NotificationService
from app.utils.sanitizer import sanitize_text
from app.schemas.rating import RatingCreateRequest


class RatingService:
    def __init__(self, db: Session):
        self.db = db
        self.rating_repo = RatingRepository(db)
        self.booking_repo = BookingRepository(db)
        self.mentor_repo = MentorRepository(db)
        self.notification_service = NotificationService(db)

    def create_rating(self, student: Student, payload: RatingCreateRequest) -> Rating:
        booking = self.booking_repo.get(payload.booking_id)
        if booking is None or booking.student_id != student.id:
            raise NotFoundException("Booking not found.")

        if booking.status != BookingStatus.COMPLETED:
            raise BadRequestException("You can only rate a session after it has been completed.")

        existing = self.rating_repo.get_by_booking_id(booking.id)
        if existing is not None:
            raise ConflictException("You have already rated this booking.")

        rating = self.rating_repo.create({
            "booking_id": booking.id,
            "student_id": student.id,
            "mentor_id": booking.mentor_id,
            "score": payload.score,
            "review": sanitize_text(payload.review),
        })

        # Recompute and persist denormalized aggregate stats on the mentor
        avg_score, total = self.rating_repo.get_mentor_aggregate(booking.mentor_id)
        mentor = self.mentor_repo.get(booking.mentor_id)
        if mentor is not None:
            mentor.average_rating = round(avg_score, 2)
            mentor.total_ratings = total
            self.db.add(mentor)
            self.db.commit()

            self.notification_service.notify(
                mentor.user_id, NotificationType.SYSTEM, "You received a new rating",
                body=f"A student rated your session {payload.score}/5.", reference_id=rating.id,
            )

        return rating

    def list_for_mentor(self, mentor_id: int, skip: int = 0, limit: int = 20) -> List[Rating]:
        return self.rating_repo.list_by_mentor(mentor_id, skip, limit)

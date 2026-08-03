"""
app/models/rating.py
----------------------
Student's rating/review of a mentor after a completed booking.
One rating per booking (enforced via unique constraint on booking_id).
Aggregate stats are denormalized onto Mentor.average_rating / total_ratings.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship

from app.db.base_class import Base, TimestampMixin


class Rating(Base, TimestampMixin):
    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id", ondelete="CASCADE"),
                         unique=True, nullable=False, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id", ondelete="CASCADE"), nullable=False, index=True)

    score = Column(Integer, nullable=False)   # 1 to 5
    review = Column(Text, nullable=True)

    booking = relationship("Booking", back_populates="rating")
    student = relationship("Student", back_populates="ratings_given")
    mentor = relationship("Mentor", back_populates="ratings_received")

    __table_args__ = (
        CheckConstraint("score >= 1 AND score <= 5", name="ck_rating_score_range"),
    )

    def __repr__(self) -> str:
        return f"<Rating id={self.id} mentor_id={self.mentor_id} score={self.score}>"

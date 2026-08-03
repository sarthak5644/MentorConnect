"""
app/services/booking_service.py
-----------------------------------
Business logic for students booking mentor availability slots, and for
mentors/students managing booking lifecycle (cancel, complete, no-show).
"""

from typing import List, Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import NotFoundException, ConflictException, ForbiddenException, BadRequestException
from app.models.enums import SlotStatus, BookingStatus, NotificationType
from app.models.booking import Booking
from app.models.student import Student
from app.repositories.booking_repository import BookingRepository
from app.repositories.slot_repository import SlotRepository
from app.services.notification_service import NotificationService
from app.services.audit_service import AuditService
from app.utils.sanitizer import sanitize_text
from app.schemas.booking import BookingCreateRequest


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.slot_repo = SlotRepository(db)
        self.notification_service = NotificationService(db)
        self.audit_service = AuditService(db)

    def create_booking(self, student: Student, payload: BookingCreateRequest) -> Booking:
        slot = self.slot_repo.get(payload.slot_id)
        if slot is None:
            raise NotFoundException("Availability slot not found.")

        if slot.status != SlotStatus.AVAILABLE:
            raise ConflictException("This slot is no longer available for booking.")

        if slot.start_time <= datetime.utcnow():
            raise BadRequestException("Cannot book a slot that has already started or passed.")

        # Flip slot to BOOKED first - if the booking insert below fails due to a race
        # (another request booked it concurrently), the unique constraint on
        # bookings.slot_id will raise IntegrityError and we roll back cleanly.
        slot.status = SlotStatus.BOOKED
        self.db.add(slot)

        try:
            booking = self.booking_repo.create({
                "student_id": student.id,
                "mentor_id": slot.mentor_id,
                "slot_id": slot.id,
                "status": BookingStatus.SCHEDULED,
                "notes": sanitize_text(payload.notes),
            })
        except IntegrityError:
            self.db.rollback()
            raise ConflictException("This slot was just booked by someone else. Please choose another slot.")

        self.notification_service.notify(
            slot.mentor.user_id if slot.mentor else None, NotificationType.BOOKING,
            "New session booked", body=f"A student booked your session on {slot.start_time}.",
            reference_id=booking.id,
        )
        return booking

    def cancel_booking(self, actor_user_id: int, booking_id: int, reason: str, is_admin: bool = False) -> Booking:
        booking = self.booking_repo.get(booking_id)
        if booking is None:
            raise NotFoundException("Booking not found.")

        if not is_admin:
            owns_as_student = booking.student and booking.student.user_id == actor_user_id
            owns_as_mentor = booking.mentor and booking.mentor.user_id == actor_user_id
            if not (owns_as_student or owns_as_mentor):
                raise ForbiddenException("You are not authorized to cancel this booking.")

        if booking.status != BookingStatus.SCHEDULED:
            raise ConflictException(f"Cannot cancel a booking that is already {booking.status.value}.")

        booking.status = BookingStatus.CANCELLED
        booking.cancelled_at = datetime.utcnow()
        booking.cancellation_reason = sanitize_text(reason)
        self.db.add(booking)

        # Free up the slot again so it can be rebooked
        slot = self.slot_repo.get(booking.slot_id)
        if slot is not None:
            slot.status = SlotStatus.AVAILABLE
            self.db.add(slot)

        self.db.commit()
        self.db.refresh(booking)

        notify_user_id = (
            booking.mentor.user_id if booking.student and booking.student.user_id == actor_user_id
            else (booking.student.user_id if booking.student else None)
        )
        if notify_user_id:
            self.notification_service.notify(
                notify_user_id, NotificationType.BOOKING, "Booking cancelled",
                body=reason, reference_id=booking.id,
            )
        return booking

    def mark_completed(self, mentor_user_id: int, booking_id: int) -> Booking:
        booking = self.booking_repo.get(booking_id)
        if booking is None or not booking.mentor or booking.mentor.user_id != mentor_user_id:
            raise NotFoundException("Booking not found.")
        if booking.status != BookingStatus.SCHEDULED:
            raise ConflictException(f"Cannot mark a {booking.status.value} booking as completed.")

        booking.status = BookingStatus.COMPLETED
        self.db.add(booking)

        booking.mentor.total_sessions_completed += 1
        self.db.add(booking.mentor)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def mark_no_show(self, mentor_user_id: int, booking_id: int) -> Booking:
        booking = self.booking_repo.get(booking_id)
        if booking is None or not booking.mentor or booking.mentor.user_id != mentor_user_id:
            raise NotFoundException("Booking not found.")
        if booking.status != BookingStatus.SCHEDULED:
            raise ConflictException(f"Cannot mark a {booking.status.value} booking as no-show.")

        booking.status = BookingStatus.NO_SHOW
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking

    def list_for_student(self, student_id: int, skip: int = 0, limit: int = 20) -> List[Booking]:
        return self.booking_repo.list_by_student(student_id, skip, limit)

    def list_for_mentor(
        self, mentor_id: int, status: Optional[BookingStatus] = None, skip: int = 0, limit: int = 20
    ) -> List[Booking]:
        return self.booking_repo.list_by_mentor(mentor_id, status, skip, limit)

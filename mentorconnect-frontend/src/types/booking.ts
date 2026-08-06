import { BookingStatus } from './enums';
import { AvailabilitySlot } from './availability';

export interface Booking {
  id: number;
  student_id: number;
  mentor_id: number;
  slot: AvailabilitySlot;
  status: BookingStatus;
  meeting_link?: string | null;
  notes?: string | null;
  cancelled_at?: string | null;
  cancellation_reason?: string | null;
  created_at: string;
}

export interface CreateBookingRequest {
  slot_id: number;
  notes?: string;
}

export interface CancelBookingRequest {
  cancellation_reason: string;
}

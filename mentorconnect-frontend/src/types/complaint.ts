import { ComplaintStatus } from './enums';

export interface Complaint {
  id: number;
  student_id: number;
  against_user_id?: number | null;
  booking_id?: number | null;
  subject: string;
  description: string;
  status: ComplaintStatus;
  admin_notes?: string | null;
  resolved_at?: string | null;
  created_at: string;
}

export interface CreateComplaintRequest {
  against_user_id?: number;
  booking_id?: number;
  subject: string;
  description: string;
}
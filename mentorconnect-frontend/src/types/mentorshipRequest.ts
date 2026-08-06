import { MentorshipRequestStatus } from './enums';
import { Mentor } from './mentor';
import { Student } from './student';

export interface MentorshipRequest {
  id: number;
  student: Student;
  mentor: Mentor;
  message?: string | null;
  status: MentorshipRequestStatus;
  responded_at?: string | null;
  response_note?: string | null;
  created_at: string;
}

export interface CreateMentorshipRequest {
  mentor_id: number;
  message?: string;
}

export interface RespondMentorshipRequest {
  status: MentorshipRequestStatus.ACCEPTED | MentorshipRequestStatus.REJECTED;
  response_note?: string;
}
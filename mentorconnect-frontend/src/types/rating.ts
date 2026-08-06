export interface Rating {
  id: number;
  booking_id: number;
  student_id: number;
  mentor_id: number;
  score: number;
  review?: string | null;
  created_at: string;
}

export interface CreateRatingRequest {
  booking_id: number;
  score: number;
  review?: string;
}
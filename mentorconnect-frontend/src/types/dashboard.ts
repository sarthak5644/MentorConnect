export interface AdminAnalytics {
  total_students: number;
  total_mentors: number;
  pending_mentor_approvals: number;
  total_bookings: number;
  total_completed_sessions: number;
  open_complaints: number;
  new_users_last_30_days: number;
  revenue_estimate?: number;
}

export interface StudentDashboard {
  active_requests: number;
  upcoming_bookings: number;
  unread_notifications: number;
  unread_messages: number;
}

export interface MentorDashboard {
  pending_requests: number;
  upcoming_bookings: number;
  total_students_mentored: number;
  average_rating: number;
  unread_notifications: number;
}
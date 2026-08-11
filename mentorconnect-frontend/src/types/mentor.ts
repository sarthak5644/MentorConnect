import { MentorApprovalStatus } from './enums';
import { User } from './user';
import { Field } from './category';

export interface Qualification {
  degree: string;
  institute: string;
  year: number;
}

export interface Achievement {
  title: string;
  description?: string;
  year?: number;
}

// Matches the backend's MentorOut exactly: a flat user_id (not a nested
// user object — that only appears in MentorProfileResponse for /mentors/me),
// and qualifications/achievements come back as raw JSON strings, not
// parsed arrays (parse with JSON.parse when rendering).
export interface Mentor {
  id: number;
  user_id: number;
  headline?: string | null;
  bio?: string | null;
  years_of_experience: number;
  current_organization?: string | null;
  designation?: string | null;
  qualifications?: string | null;
  achievements?: string | null;
  hourly_rate: number;
  city?: string | null;
  country?: string | null;
  linkedin_url?: string | null;
  portfolio_url?: string | null;
  approval_status: MentorApprovalStatus;
  average_rating: number;
  total_ratings: number;
  total_sessions_completed: number;
  is_accepting_requests: boolean;
  expertise_fields: Field[];
  created_at: string;
}

// Lightweight shape returned by /mentors/search — a subset of Mentor,
// used for search-result cards.
export interface MentorCard {
  id: number;
  headline?: string | null;
  years_of_experience: number;
  current_organization?: string | null;
  designation?: string | null;
  hourly_rate: number;
  city?: string | null;
  country?: string | null;
  average_rating: number;
  total_ratings: number;
  is_accepting_requests: boolean;
  expertise_fields: Field[];
}

// GET /mentors/me returns account info + mentor profile as two separate
// objects, not one merged Mentor.
export interface MentorProfileResponse {
  user: User;
  profile: Mentor;
}

export interface MentorSearchFilters {
  keyword?: string;
  field_id?: number;
  category_id?: number;
  min_rating?: number;
  max_hourly_rate?: number;
  min_experience?: number;
  city?: string;
  country?: string;
  is_accepting_requests?: boolean;
  page?: number;
  page_size?: number;
}

export interface MentorProfileUpdateRequest {
  headline?: string;
  bio?: string;
  years_of_experience?: number;
  current_organization?: string;
  designation?: string;
  hourly_rate?: number;
  city?: string;
  country?: string;
  linkedin_url?: string;
  portfolio_url?: string;
}

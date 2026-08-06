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
  description: string;
  year: number;
}

export interface Mentor {
  id: number;
  user: User;
  headline?: string | null;
  bio?: string | null;
  years_of_experience: number;
  current_organization?: string | null;
  designation?: string | null;
  qualifications: Qualification[];
  achievements: Achievement[];
  hourly_rate: number;
  city?: string | null;
  country?: string | null;
  linkedin_url?: string | null;
  portfolio_url?: string | null;
  approval_status: MentorApprovalStatus;
  rejection_reason?: string | null;
  average_rating: number;
  total_ratings: number;
  total_sessions_completed: number;
  is_accepting_requests: boolean;
  expertise_fields: Field[];
  created_at: string;
}

export interface MentorSearchFilters {
  search?: string;
  field_id?: number;
  category_id?: number;
  min_rating?: number;
  max_hourly_rate?: number;
  city?: string;
  sort_by?: 'rating' | 'experience' | 'price_low' | 'price_high';
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
  expertise_field_ids?: number[];
}
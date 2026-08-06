import { User } from './user';

export interface Student {
  id: number;
  user: User;
  institution_name?: string | null;
  education_level?: string | null;
  field_of_study?: string | null;
  date_of_birth?: string | null;
  bio?: string | null;
  city?: string | null;
  country?: string | null;
  interests?: string | null;
}

export interface StudentProfileUpdateRequest {
  institution_name?: string;
  education_level?: string;
  field_of_study?: string;
  date_of_birth?: string;
  bio?: string;
  city?: string;
  country?: string;
  interests?: string;
}
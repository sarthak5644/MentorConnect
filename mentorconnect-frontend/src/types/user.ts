import { RoleName, UserStatus } from './enums';

export interface Role {
  id: number;
  name: RoleName;
  description?: string | null;
}

export interface User {
  id: number;
  full_name: string;
  email: string;
  mobile_number?: string | null;
  role: Role;
  status: UserStatus;
  is_email_verified: boolean;
  is_mobile_verified: boolean;
  profile_image_url?: string | null;
  last_login_at?: string | null;
  created_at: string;
}

// The backend gates login behind a captcha, same as registration.
export interface LoginRequest {
  email: string;
  password: string;
  captcha_session_id: string;
  captcha_answer: string;
}

// Registration is split into two distinct backend endpoints
// (/auth/register/student, /auth/register/mentor) with different optional
// fields — there is no single unified "role" registration payload.
export interface StudentRegisterRequest {
  full_name: string;
  email: string;
  mobile_number: string;
  password: string;
  captcha_session_id: string;
  captcha_answer: string;
  institution_name?: string;
  education_level?: string;
  field_of_study?: string;
}

export interface MentorRegisterRequest {
  full_name: string;
  email: string;
  mobile_number: string;
  password: string;
  captcha_session_id: string;
  captcha_answer: string;
  headline?: string;
  years_of_experience: number;
  current_organization?: string;
  designation?: string;
  hourly_rate: number;
  expertise_field_ids: number[];
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// Real shape is { user, tokens }, not a flat object with the user spread
// alongside the tokens.
export interface LoginResponse {
  user: User;
  tokens: AuthTokens;
}

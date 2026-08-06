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

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  full_name: string;
  email: string;
  mobile_number?: string;
  password: string;
  role: RoleName.MENTOR | RoleName.STUDENT;
  captcha_session_id: string;
  captcha_answer: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface AuthResponse extends AuthTokens {
  user: User;
}
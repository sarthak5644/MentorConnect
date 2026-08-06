export interface CaptchaResponse {
  session_id: string;
  image_base64: string;
}

export interface RequestOtpRequest {
  destination: string;
  purpose: string;
}

export interface VerifyOtpRequest {
  destination: string;
  otp: string;
  purpose: string;
}

export interface ForgotPasswordRequest {
  email: string;
}

export interface ResetPasswordRequest {
  email: string;
  otp: string;
  new_password: string;
}
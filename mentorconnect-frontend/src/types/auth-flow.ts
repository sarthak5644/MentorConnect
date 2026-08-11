export interface CaptchaResponse {
  session_id: string;
  image_base64: string;
  expires_in_seconds: number;
}

// The backend has two separate send endpoints (email vs mobile), each with
// a differently-named destination field — not a single generic
// { destination, purpose }.
export interface EmailOtpRequest {
  email: string;
  purpose: string;
}

export interface MobileOtpRequest {
  mobile_number: string;
  purpose: string;
}

export interface VerifyOtpRequest {
  destination: string;
  otp_code: string;
  purpose: string;
}

export interface ForgotPasswordRequest {
  email: string;
  captcha_session_id: string;
  captcha_answer: string;
}

export interface ResetPasswordRequest {
  email: string;
  otp_code: string;
  password: string;
}

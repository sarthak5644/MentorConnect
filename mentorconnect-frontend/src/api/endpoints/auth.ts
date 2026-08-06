import { apiClient } from '../client';
import {
  LoginRequest, RegisterRequest, AuthResponse, CaptchaResponse,
  RequestOtpRequest, VerifyOtpRequest, ForgotPasswordRequest,
  ResetPasswordRequest, MessageResponse,
} from '@/types';

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<AuthResponse>('/auth/login', data).then((r) => r.data),

  register: (data: RegisterRequest) =>
    apiClient.post<AuthResponse>('/auth/register', data).then((r) => r.data),

  logout: () => apiClient.post<MessageResponse>('/auth/logout').then((r) => r.data),

  getCaptcha: () => apiClient.get<CaptchaResponse>('/auth/captcha').then((r) => r.data),

  requestOtp: (data: RequestOtpRequest) =>
    apiClient.post<MessageResponse>('/auth/otp/request', data).then((r) => r.data),

  verifyOtp: (data: VerifyOtpRequest) =>
    apiClient.post<MessageResponse>('/auth/otp/verify', data).then((r) => r.data),

  forgotPassword: (data: ForgotPasswordRequest) =>
    apiClient.post<MessageResponse>('/auth/forgot-password', data).then((r) => r.data),

  resetPassword: (data: ResetPasswordRequest) =>
    apiClient.post<MessageResponse>('/auth/reset-password', data).then((r) => r.data),

  getMe: () => apiClient.get('/auth/me').then((r) => r.data),
};
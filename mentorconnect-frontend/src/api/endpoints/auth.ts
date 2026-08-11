import { apiClient } from '../client';
import {
  LoginRequest, StudentRegisterRequest, MentorRegisterRequest, LoginResponse, CaptchaResponse,
  EmailOtpRequest, MobileOtpRequest, VerifyOtpRequest, ForgotPasswordRequest,
  ResetPasswordRequest, MessageResponse, User,
} from '@/types';

export const authApi = {
  login: (data: LoginRequest) =>
    apiClient.post<LoginResponse>('/auth/login', data).then((r) => r.data),

  registerStudent: (data: StudentRegisterRequest) =>
    apiClient.post<User>('/auth/register/student', data).then((r) => r.data),

  registerMentor: (data: MentorRegisterRequest) =>
    apiClient.post<User>('/auth/register/mentor', data).then((r) => r.data),

  logout: (refreshToken: string) =>
    apiClient.post<MessageResponse>('/auth/logout', { refresh_token: refreshToken }).then((r) => r.data),

  getCaptcha: () => apiClient.get<CaptchaResponse>('/auth/captcha').then((r) => r.data),

  sendEmailOtp: (data: EmailOtpRequest) =>
    apiClient.post<MessageResponse>('/otp/email/send', data).then((r) => r.data),

  sendMobileOtp: (data: MobileOtpRequest) =>
    apiClient.post<MessageResponse>('/otp/mobile/send', data).then((r) => r.data),

  verifyOtp: (data: VerifyOtpRequest) =>
    apiClient.post<MessageResponse>('/otp/verify', data).then((r) => r.data),

  forgotPassword: (data: ForgotPasswordRequest) =>
    apiClient.post<MessageResponse>('/auth/forgot-password', data).then((r) => r.data),

  resetPassword: (data: ResetPasswordRequest) =>
    apiClient.post<MessageResponse>('/auth/reset-password', data).then((r) => r.data),

  getMe: () => apiClient.get<User>('/auth/me').then((r) => r.data),
};

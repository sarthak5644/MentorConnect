import { apiClient } from '../client';
import {
  AdminAnalytics, Mentor, User, MentorApprovalStatus, UserStatus,
  PaginatedResponse, PaginationParams, AuditLog,
} from '@/types';

export const adminApi = {
  getAnalytics: () => apiClient.get<AdminAnalytics>('/admin/analytics').then((r) => r.data),

  listPendingMentors: (params?: PaginationParams) =>
    apiClient.get<PaginatedResponse<Mentor>>('/admin/mentors/pending', { params }).then((r) => r.data),

  approveMentor: (mentorId: number) =>
    apiClient.patch<Mentor>(`/admin/mentors/${mentorId}/approve`).then((r) => r.data),

  rejectMentor: (mentorId: number, reason: string) =>
    apiClient.patch<Mentor>(`/admin/mentors/${mentorId}/reject`, { rejection_reason: reason }).then((r) => r.data),

  listMentors: (params?: PaginationParams & { approval_status?: MentorApprovalStatus; search?: string }) =>
    apiClient.get<PaginatedResponse<Mentor>>('/admin/mentors', { params }).then((r) => r.data),

  listStudents: (params?: PaginationParams & { search?: string }) =>
    apiClient.get<PaginatedResponse<User>>('/admin/students', { params }).then((r) => r.data),

  listUsers: (params?: PaginationParams & { search?: string; status?: UserStatus }) =>
    apiClient.get<PaginatedResponse<User>>('/admin/users', { params }).then((r) => r.data),

  blockUser: (userId: number, reason: string) =>
    apiClient.patch<User>(`/admin/users/${userId}/block`, { blocked_reason: reason }).then((r) => r.data),

  unblockUser: (userId: number) =>
    apiClient.patch<User>(`/admin/users/${userId}/unblock`).then((r) => r.data),

  verifyDocument: (documentId: number) =>
    apiClient.patch(`/admin/documents/${documentId}/verify`).then((r) => r.data),

  rejectDocument: (documentId: number, reason: string) =>
    apiClient.patch(`/admin/documents/${documentId}/reject`, { rejection_reason: reason }).then((r) => r.data),

  listAuditLogs: (params?: PaginationParams & { action?: string; entity_type?: string }) =>
    apiClient.get<PaginatedResponse<AuditLog>>('/admin/audit-logs', { params }).then((r) => r.data),
};
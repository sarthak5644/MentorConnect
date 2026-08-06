import { apiClient } from '../client';
import {
  MentorshipRequest, CreateMentorshipRequest, RespondMentorshipRequest,
  PaginatedResponse, PaginationParams,
} from '@/types';

export const mentorshipRequestsApi = {
  create: (data: CreateMentorshipRequest) =>
    apiClient.post<MentorshipRequest>('/mentorship-requests', data).then((r) => r.data),

  listMine: (params?: PaginationParams) =>
    apiClient.get<PaginatedResponse<MentorshipRequest>>('/mentorship-requests', { params }).then((r) => r.data),

  getById: (id: number) =>
    apiClient.get<MentorshipRequest>(`/mentorship-requests/${id}`).then((r) => r.data),

  respond: (id: number, data: RespondMentorshipRequest) =>
    apiClient.patch<MentorshipRequest>(`/mentorship-requests/${id}/respond`, data).then((r) => r.data),

  cancel: (id: number) =>
    apiClient.patch<MentorshipRequest>(`/mentorship-requests/${id}/cancel`).then((r) => r.data),
};
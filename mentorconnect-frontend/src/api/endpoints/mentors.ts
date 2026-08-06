import { apiClient } from '../client';
import { Mentor, MentorSearchFilters, MentorProfileUpdateRequest, PaginatedResponse } from '@/types';

export const mentorsApi = {
  search: (filters: MentorSearchFilters) =>
    apiClient.get<PaginatedResponse<Mentor>>('/mentors', { params: filters }).then((r) => r.data),

  getById: (id: number) =>
    apiClient.get<Mentor>(`/mentors/${id}`).then((r) => r.data),

  getMyProfile: () =>
    apiClient.get<Mentor>('/mentors/me').then((r) => r.data),

  updateProfile: (data: MentorProfileUpdateRequest) =>
    apiClient.patch<Mentor>('/mentors/me', data).then((r) => r.data),

  uploadDocument: (formData: FormData) =>
    apiClient.post('/mentors/me/documents', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data),

  getMyDocuments: () =>
    apiClient.get('/mentors/me/documents').then((r) => r.data),
};


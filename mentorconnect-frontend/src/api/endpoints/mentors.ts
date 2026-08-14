import { apiClient } from '../client';
import { Mentor, MentorCard, MentorProfileResponse, MentorSearchFilters, MentorProfileUpdateRequest, PaginatedResponse } from '@/types';

export const mentorsApi = {
  search: (filters: MentorSearchFilters) =>
    apiClient.get<PaginatedResponse<MentorCard>>('/mentors/search', { params: filters }).then((r) => r.data),

  getById: (id: number) =>
    apiClient.get<Mentor>(`/mentors/${id}`).then((r) => r.data),

  getMyProfile: () =>
    apiClient.get<MentorProfileResponse>('/mentors/me').then((r) => r.data),

  updateProfile: (data: MentorProfileUpdateRequest) =>
    apiClient.put<Mentor>('/mentors/me', data).then((r) => r.data),

  updateQualifications: (qualifications: { degree: string; institute: string; year: number }[]) =>
    apiClient.put<Mentor>('/mentors/me/qualifications', { qualifications }).then((r) => r.data),

  updateAchievements: (achievements: { title: string; description?: string; year?: number }[]) =>
    apiClient.put<Mentor>('/mentors/me/achievements', { achievements }).then((r) => r.data),

  updateExpertise: (field_ids: number[]) =>
    apiClient.put<Mentor>('/mentors/me/expertise', { field_ids }).then((r) => r.data),

  uploadDocument: (formData: FormData, documentType: string) =>
    apiClient.post(`/mentors/me/documents?document_type=${encodeURIComponent(documentType)}`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data),

  getMyDocuments: () =>
    apiClient.get('/mentors/me/documents').then((r) => r.data),
};

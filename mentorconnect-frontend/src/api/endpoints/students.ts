import { apiClient } from '../client';
import { Student, StudentProfileUpdateRequest } from '@/types';

export const studentsApi = {
  getMyProfile: () => apiClient.get<Student>('/students/me').then((r) => r.data),
  updateProfile: (data: StudentProfileUpdateRequest) =>
    apiClient.patch<Student>('/students/me', data).then((r) => r.data),
};
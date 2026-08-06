import { apiClient } from '../client';
import { StudentDashboard, MentorDashboard } from '@/types';

export const dashboardApi = {
  getStudentDashboard: () =>
    apiClient.get<StudentDashboard>('/dashboard/student').then((r) => r.data),
  getMentorDashboard: () =>
    apiClient.get<MentorDashboard>('/dashboard/mentor').then((r) => r.data),
};
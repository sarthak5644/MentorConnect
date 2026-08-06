import { apiClient } from '../client';
import { Notification, PaginatedResponse, PaginationParams } from '@/types';

export const notificationsApi = {
  list: (params?: PaginationParams) =>
    apiClient.get<PaginatedResponse<Notification>>('/notifications', { params }).then((r) => r.data),
  markRead: (id: number) =>
    apiClient.patch<Notification>(`/notifications/${id}/read`).then((r) => r.data),
  markAllRead: () =>
    apiClient.patch('/notifications/read-all').then((r) => r.data),
  unreadCount: () =>
    apiClient.get<{ count: number }>('/notifications/unread-count').then((r) => r.data),
};
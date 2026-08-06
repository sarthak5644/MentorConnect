import { apiClient } from '../client';
import { Complaint, CreateComplaintRequest, ComplaintStatus, PaginatedResponse, PaginationParams } from '@/types';

export const complaintsApi = {
  create: (data: CreateComplaintRequest) =>
    apiClient.post<Complaint>('/complaints', data).then((r) => r.data),
  listMine: (params?: PaginationParams) =>
    apiClient.get<PaginatedResponse<Complaint>>('/complaints/me', { params }).then((r) => r.data),
  listAll: (params?: PaginationParams & { status?: ComplaintStatus }) =>
    apiClient.get<PaginatedResponse<Complaint>>('/complaints', { params }).then((r) => r.data),
  resolve: (id: number, data: { status: ComplaintStatus; admin_notes?: string }) =>
    apiClient.patch<Complaint>(`/complaints/${id}/resolve`, data).then((r) => r.data),
};
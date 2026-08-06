import { apiClient } from '../client';
import { Rating, CreateRatingRequest, PaginatedResponse, PaginationParams } from '@/types';

export const ratingsApi = {
  create: (data: CreateRatingRequest) =>
    apiClient.post<Rating>('/ratings', data).then((r) => r.data),
  listForMentor: (mentorId: number, params?: PaginationParams) =>
    apiClient.get<PaginatedResponse<Rating>>(`/ratings/mentor/${mentorId}`, { params }).then((r) => r.data),
  listMine: (params?: PaginationParams) =>
    apiClient.get<PaginatedResponse<Rating>>('/ratings/me', { params }).then((r) => r.data),
};
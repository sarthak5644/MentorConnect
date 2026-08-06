import { apiClient } from '../client';
import { Booking, CreateBookingRequest, CancelBookingRequest, PaginatedResponse, PaginationParams } from '@/types';

export const bookingsApi = {
  create: (data: CreateBookingRequest) =>
    apiClient.post<Booking>('/bookings', data).then((r) => r.data),
  listMine: (params?: PaginationParams) =>
    apiClient.get<PaginatedResponse<Booking>>('/bookings', { params }).then((r) => r.data),
  getById: (id: number) => apiClient.get<Booking>(`/bookings/${id}`).then((r) => r.data),
  cancel: (id: number, data: CancelBookingRequest) =>
    apiClient.patch<Booking>(`/bookings/${id}/cancel`, data).then((r) => r.data),
  complete: (id: number) =>
    apiClient.patch<Booking>(`/bookings/${id}/complete`).then((r) => r.data),
};
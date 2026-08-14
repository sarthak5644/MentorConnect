import { apiClient } from '../client';
import { Rating, CreateRatingRequest, PaginationParams } from '@/types';

// Note: the backend has no /ratings/me — there is no endpoint to list a
// student's own submitted ratings. If "have I rated this booking" needs
// checking, track it client-side after a successful create, and otherwise
// let the backend's 409 (already rated) surface via extractErrorMessage.
export const ratingsApi = {
  create: (data: CreateRatingRequest) =>
    apiClient.post<Rating>('/ratings', data).then((r) => r.data),
  // Backend accepts page/page_size but its response is a plain array, not a
  // paginated envelope with total/total_pages.
  listForMentor: (mentorId: number, params?: PaginationParams) =>
    apiClient.get<Rating[]>(`/ratings/mentor/${mentorId}`, { params }).then((r) => r.data),
};

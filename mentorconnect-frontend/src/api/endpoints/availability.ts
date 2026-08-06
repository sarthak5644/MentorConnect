import { apiClient } from '../client';
import { AvailabilitySlot, CreateSlotRequest } from '@/types';

export const availabilityApi = {
  listMySlots: () => apiClient.get<AvailabilitySlot[]>('/availability/me').then((r) => r.data),
  listMentorSlots: (mentorId: number) =>
    apiClient.get<AvailabilitySlot[]>(`/availability/mentor/${mentorId}`).then((r) => r.data),
  create: (data: CreateSlotRequest) =>
    apiClient.post<AvailabilitySlot>('/availability', data).then((r) => r.data),
  delete: (id: number) => apiClient.delete(`/availability/${id}`).then((r) => r.data),
};
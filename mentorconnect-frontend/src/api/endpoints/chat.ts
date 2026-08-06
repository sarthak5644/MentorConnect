import { apiClient } from '../client';
import { Chat, Message, SendMessageRequest } from '@/types';

export const chatApi = {
  getByRequestId: (mentorshipRequestId: number) =>
    apiClient.get<Chat>(`/chats/by-request/${mentorshipRequestId}`).then((r) => r.data),
  listMessages: (chatId: number) =>
    apiClient.get<Message[]>(`/chats/${chatId}/messages`).then((r) => r.data),
  sendMessage: (chatId: number, data: SendMessageRequest) =>
    apiClient.post<Message>(`/chats/${chatId}/messages`, data).then((r) => r.data),
  sendAttachment: (chatId: number, formData: FormData) =>
    apiClient.post<Message>(`/chats/${chatId}/messages/attachment`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }).then((r) => r.data),
  markRead: (chatId: number) =>
    apiClient.patch(`/chats/${chatId}/read`).then((r) => r.data),
  listMyChats: () => apiClient.get<Chat[]>('/chats').then((r) => r.data),
};
import { apiClient } from '../client';
import { Category, Field } from '@/types';

export const categoriesApi = {
  list: () => apiClient.get<Category[]>('/categories').then((r) => r.data),
  create: (data: { name: string; description?: string }) =>
    apiClient.post<Category>('/categories', data).then((r) => r.data),
  update: (id: number, data: { name?: string; description?: string; is_active?: boolean }) =>
    apiClient.patch<Category>(`/categories/${id}`, data).then((r) => r.data),
  delete: (id: number) => apiClient.delete(`/categories/${id}`).then((r) => r.data),
  createField: (categoryId: number, data: { name: string }) =>
    apiClient.post<Field>(`/categories/${categoryId}/fields`, data).then((r) => r.data),
  updateField: (fieldId: number, data: { name?: string; is_active?: boolean }) =>
    apiClient.patch<Field>(`/categories/fields/${fieldId}`, data).then((r) => r.data),
  deleteField: (fieldId: number) => apiClient.delete(`/categories/fields/${fieldId}`).then((r) => r.data),
};
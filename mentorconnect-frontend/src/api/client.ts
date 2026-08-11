import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { store } from '@/store';
import { logout, setTokens } from '@/store/authSlice';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = store.getState().auth.accessToken;
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// The backend wraps every response as { success, message, data } and every
// paginated list as { success, message, data: T[], total, page, page_size,
// total_pages } (array under `data`, not `items`). This app's endpoint files
// were written expecting the bare payload (and `items` for lists), so we
// reshape here once instead of touching every endpoint file.
apiClient.interceptors.response.use((response) => {
  const body = response.data;
  if (body && typeof body === 'object' && 'success' in body && 'data' in body) {
    if ('total' in body && 'page_size' in body) {
      response.data = {
        items: body.data,
        total: body.total,
        page: body.page,
        page_size: body.page_size,
        total_pages: body.total_pages,
      };
    } else {
      response.data = body.data !== null && body.data !== undefined ? body.data : { message: body.message };
    }
  }
  return response;
});

let isRefreshing = false;
let refreshQueue: Array<(token: string) => void> = [];

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry && originalRequest.url !== '/auth/refresh') {
      if (isRefreshing) {
        return new Promise((resolve) => {
          refreshQueue.push((token: string) => {
            if (originalRequest.headers) originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(apiClient(originalRequest));
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const refreshToken = store.getState().auth.refreshToken;
        if (!refreshToken) throw new Error('No refresh token');

        // Raw axios (not apiClient) so the response-unwrap interceptor above
        // doesn't apply here — unwrap this one manually.
        const { data: envelope } = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        const tokens = envelope.data;

        store.dispatch(setTokens({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token }));
        refreshQueue.forEach((cb) => cb(tokens.access_token));
        refreshQueue = [];

        if (originalRequest.headers) originalRequest.headers.Authorization = `Bearer ${tokens.access_token}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        store.dispatch(logout());
        window.location.href = '/login';
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

/** Backend error envelope is always { success: false, error_code, message, details }. */
export function extractErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as { message?: string; details?: unknown } | undefined;
    if (data?.message) return data.message;
    return error.message || 'Something went wrong';
  }
  return 'Something went wrong';
}

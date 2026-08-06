export interface ApiError {
  detail: string | { msg: string; loc: (string | number)[] }[];
  status_code?: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginationParams {
  page?: number;
  page_size?: number;
}

export interface MessageResponse {
  message: string;
}
import { NotificationType } from './enums';

export interface Notification {
  id: number;
  user_id: number;
  type: NotificationType;
  title: string;
  body?: string | null;
  reference_id?: number | null;
  is_read: boolean;
  created_at: string;
}
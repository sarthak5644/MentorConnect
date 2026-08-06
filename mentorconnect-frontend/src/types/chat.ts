import { MessageType } from './enums';

export interface Chat {
  id: number;
  mentorship_request_id: number;
  is_active: boolean;
  last_message_at?: string | null;
}

export interface Message {
  id: number;
  chat_id: number;
  sender_id: number;
  message_type: MessageType;
  content?: string | null;
  attachment_path?: string | null;
  is_read: boolean;
  created_at: string;
}

export interface SendMessageRequest {
  content?: string;
  message_type?: MessageType;
}
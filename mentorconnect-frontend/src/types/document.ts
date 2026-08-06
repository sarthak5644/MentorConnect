import { DocumentStatus } from './enums';

export interface MentorDocument {
  id: number;
  mentor_id: number;
  document_type: string;
  file_name: string;
  file_path: string;
  file_size_bytes?: number | null;
  mime_type?: string | null;
  status: DocumentStatus;
  rejection_reason?: string | null;
  created_at: string;
}
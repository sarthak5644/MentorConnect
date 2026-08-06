export interface AuditLog {
  id: number;
  actor_user_id?: number | null;
  action: string;
  entity_type?: string | null;
  entity_id?: number | null;
  description?: string | null;
  ip_address?: string | null;
  created_at: string;
}
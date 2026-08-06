import { SlotStatus } from './enums';

export interface AvailabilitySlot {
  id: number;
  mentor_id: number;
  start_time: string;
  end_time: string;
  status: SlotStatus;
}

export interface CreateSlotRequest {
  start_time: string;
  end_time: string;
}
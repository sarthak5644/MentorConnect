"""
app/schemas/availability_slot.py
------------------------------------
Schemas for mentors managing their availability slots, and students viewing them.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import SlotStatus


class SlotCreateRequest(BaseModel):
    start_time: datetime
    end_time: datetime

    @model_validator(mode="after")
    def validate_time_range(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        max_duration_minutes = 240  # sanity cap: a single slot shouldn't exceed 4 hours
        duration = (self.end_time - self.start_time).total_seconds() / 60
        if duration < 10:
            raise ValueError("Slot duration must be at least 10 minutes")
        if duration > max_duration_minutes:
            raise ValueError(f"Slot duration cannot exceed {max_duration_minutes} minutes")
        return self


class BulkSlotCreateRequest(BaseModel):
    slots: List[SlotCreateRequest] = Field(..., min_length=1, max_length=50)


class SlotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mentor_id: int
    start_time: datetime
    end_time: datetime
    status: SlotStatus


class SlotUpdateRequest(BaseModel):
    status: Optional[SlotStatus] = None

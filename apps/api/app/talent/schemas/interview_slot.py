"""Pydantic schemas for interview scheduling endpoints."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ProposeSlotRequest(BaseModel):
    """A single time slot proposal."""

    start_time: datetime
    end_time: datetime
    timezone: str = Field(..., min_length=1, max_length=50)
    meeting_url: str | None = Field(None, max_length=500)
    meeting_notes: str | None = Field(None, max_length=2000)

    @model_validator(mode="after")
    def validate_times(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time")
        return self


class ProposeSlotsRequest(BaseModel):
    """Request to propose one or more time slots."""

    slots: list[ProposeSlotRequest]

    @field_validator("slots")
    @classmethod
    def validate_slots(cls, v: list[ProposeSlotRequest]) -> list[ProposeSlotRequest]:
        if len(v) == 0:
            raise ValueError("At least one slot is required")
        if len(v) > 5:
            raise ValueError("Maximum 5 slots per proposal")
        return v


class InterviewSlotResponse(BaseModel):
    """Response for a single interview slot."""

    id: str
    interview_stage_id: str
    proposed_by: str
    start_time: datetime
    end_time: datetime
    timezone: str
    status: str
    meeting_url: str | None = None
    meeting_notes: str | None = None
    accepted_by: str | None = None
    accepted_at: datetime | None = None
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)

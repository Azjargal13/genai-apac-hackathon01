"""Planning routes for behavioral time modeling."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from energy_task_manager.tools import estimate_day_plan

router = APIRouter(prefix="/plan", tags=["plan"])


class PlanDayRequest(BaseModel):
    total_available_time_minutes: int = Field(gt=0, description="User available time for today")


@router.post("")
def plan_day(payload: PlanDayRequest) -> dict:
    return estimate_day_plan(total_available_time_minutes=payload.total_available_time_minutes)


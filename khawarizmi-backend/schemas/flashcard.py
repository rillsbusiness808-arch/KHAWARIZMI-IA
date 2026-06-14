from typing import Optional, Dict
from pydantic import BaseModel, Field


class DrillRequest(BaseModel):
    matiere:      str = "sciences_naturelles"
    nb_questions: int = Field(default=12, ge=4, le=20)


class ScheduleRequest(BaseModel):
    micro_concept_id: str
    score_percent:    float = Field(ge=0.0, le=100.0)
    fsrs_state:       Optional[Dict] = None

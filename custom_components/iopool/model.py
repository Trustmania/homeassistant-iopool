from typing import Optional, Literal
from pydantic import BaseModel
from datetime import datetime


class LatestMeasure(BaseModel):
    ecoId: str
    temperature: float
    ph: float
    orp: float
    mode: Literal["standard", "live", "maintenance", "manual", "backup", "gateway"]
    isValid: bool
    measuredAt: datetime


class Advice(BaseModel):
    filtrationDuration: Optional[float]


class Pool(BaseModel):
    id: str
    title: str
    mode: Literal["STANDARD", "OPENING", "WINTER", "INITIALIZATION"]
    hasAnActionRequired: bool
    latestMeasure: Optional[LatestMeasure]
    advice: Advice

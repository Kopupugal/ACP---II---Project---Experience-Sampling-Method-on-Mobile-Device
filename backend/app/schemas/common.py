from datetime import datetime

from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class HealthResponse(StrictModel):
    status: str
    service: str
    timestamp: datetime

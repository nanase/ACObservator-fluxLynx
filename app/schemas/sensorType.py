from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class SensorType(BaseModel):
    id: int
    created_at: datetime
    name: str = Field(..., description="センサタイプの名前")
    unit: str = Field(..., description="センサの単位")

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

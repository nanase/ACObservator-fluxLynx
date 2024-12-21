from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ObservedValue(BaseModel):
    id: int = Field(description="ID")
    created_at: datetime = Field(description="作成時刻")
    value: float = Field(description="観測値")
    sensor_type_id: int = Field(description="センサタイプのID")

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True, from_attributes=True)

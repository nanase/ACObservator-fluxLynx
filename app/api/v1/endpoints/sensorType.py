from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.sensorType import SensorType as SensorTypeModel
from app.schemas.sensorType import SensorType

router = APIRouter()


@router.get("/sensor-types/", response_model=SensorType)
def get_sensor_types(
    sensor_type_id: int = Query(..., description="取得するセンサータイプのID", alias="sensorTypeId"),
    db: Session = Depends(get_db)):
    return db.query(SensorTypeModel).filter(SensorTypeModel.id == sensor_type_id).first()


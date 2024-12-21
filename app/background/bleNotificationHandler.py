import math
import struct
from contextlib import contextmanager
from typing import Generator

from bleak.backends.characteristic import BleakGATTCharacteristic
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.observedValue import ObservedValue as ObservedValueModel
from app.models.sensorType import SensorType as SensorTypeModel

from .bleConstants import *
from .uvicornLogger import create_uvicorn_logger

logger = create_uvicorn_logger("BLENotificationHandler")


class BLENotificationHandler:
    last_voltage = math.nan
    last_frequency = math.nan

    async def handle(self, sender: BleakGATTCharacteristic, data: bytearray) -> None:
        if sender.uuid == str(BLE_CHARACTERISTIC_VOLTAGE_UUID) and len(data) == 8:
            new_voltage = struct.unpack("<d", data)[0]

            if new_voltage < 50.0 or new_voltage > 150.0:
                return

            if self.last_voltage != new_voltage:
                self.last_voltage = new_voltage
                self._add_new_observed_value("voltage")
        elif sender.uuid == str(BLE_CHARACTERISTIC_FREQ_UUID) and len(data) == 8:
            new_freq = struct.unpack("<d", data)[0]

            if new_freq < 40.0 or new_freq > 70.0:
                return

            if self.last_frequency != new_freq:
                self.last_frequency = new_freq
                self._add_new_observed_value("frequency")

    @staticmethod
    @contextmanager
    def session_scope() -> Generator[Session]:
        session = next(get_db())
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _add_new_observed_value(self, sensor_type: str) -> None:
        with self.session_scope() as session:
            existing_type = session.query(SensorTypeModel).filter(SensorTypeModel.name == sensor_type).first()

            if not existing_type:
                # 新しいセンサタイプを作成
                if sensor_type == "voltage":
                    db_sensor_type = SensorTypeModel(name="voltage", unit="Vrms")
                elif sensor_type == "frequency":
                    db_sensor_type = SensorTypeModel(name="frequency", unit="Hz")
                else:
                    raise ValueError(f"invalid sensor_type: {sensor_type}")

                session.add(db_sensor_type)
                session.commit()
                session.refresh(db_sensor_type)
                existing_type = db_sensor_type
                logger.info(f"new sensorType added: {existing_type.name} (unit: {existing_type.unit})")

            if sensor_type == "voltage":
                db_observed_value = ObservedValueModel(value=self.last_voltage, sensor_type=existing_type)
            elif sensor_type == "frequency":
                db_observed_value = ObservedValueModel(value=self.last_frequency, sensor_type=existing_type)
            else:
                raise ValueError(f"invalid sensor_type: {sensor_type}")

            session.add(db_observed_value)
            session.commit()

from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.observedValue import ObservedValue as ObservedValueModel
from app.schemas.observedValue import ObservedValue

router = APIRouter()


@router.get("/observed-values/", response_model=list[ObservedValue])
def get_observed_values(
    start: datetime | None = Query(None, description="取得するデータのISO8601形式の開始日時"),
    end: datetime | None = Query(None, description="取得するデータのISO8601形式の終了日時"),
    sensor_type_id: int | None = Query(None, description="取得するセンサータイプのID", alias="sensorTypeId"),
    offset: int | None = Query(0, description="データを読み出す開始位置"),
    limit: int | None = Query(100, description="データの取得数"),
    db: Session = Depends(get_db)):
    query = db.query(ObservedValueModel)

    if start is not None:
        if end is not None:
            if start > end:
                raise HTTPException(
                    status_code=400,
                    detail="開始日時が終了日時より後になっています。"
                )

            query = query.filter(
                ObservedValueModel.created_at >= start,
                ObservedValueModel.created_at <= end,
            )
        else:
            query = query.filter(
                ObservedValueModel.created_at >= start
            )
    elif end is not None:
        raise HTTPException(
            status_code=400,
            detail="終了日時を指定した場合は開始日時を指定する必要があります。"
        )

    if sensor_type_id is not None:
        query = query.filter(ObservedValueModel.sensor_type_id == sensor_type_id)

    if offset is not None:
        query = query.offset(offset)

    if limit is not None:
        query = query.limit(limit)

    return query.all()


@router.get(
    "/observed-values/latest",
    response_model=list[ObservedValue],
    responses={
        200: {
            "description": "センサータイプごとの最新の観測値が返されます。",
            "model": list[ObservedValue],
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 123369,
                            "sensorTypeId": 1,
                            "value": 103.044677734375,
                            "createdAt": "2024-11-29T14:45:59.973610",
                        },
                        {
                            "id": 123372,
                            "sensorTypeId": 2,
                            "value": 59.98971939086914,
                            "createdAt": "2024-11-29T14:46:02.014503",
                        },
                    ]
                }
            },
        },
    },
)
def get_latest_observed_values(db: Session = Depends(get_db)):
    """
    センサータイプごとの最新データを取得します。

    ### 概要
    - 各センサータイプの最新データを返します。
    - データが見つからない場合は空のリストを返します。

    ### パラメータ
    - **なし**

    ### レスポンス
    - センサーの種類ごとに最新のデータを1件返します。

    ### 例外
    - データがない場合でもエラーにはなりません。

    """
    subquery = (
        db.query(ObservedValueModel.sensor_type_id, func.max(ObservedValueModel.created_at).label("latest_timestamp"))
        .group_by(ObservedValueModel.sensor_type_id)
        .subquery()
    )

    # サブクエリの結果を元に詳細データを取得
    latest_data = (
        db.query(ObservedValueModel)
        .join(
            subquery,
            (ObservedValueModel.sensor_type_id == subquery.c.sensor_type_id)
            & (ObservedValueModel.created_at == subquery.c.latest_timestamp),
        )
        .all()
    )

    if not latest_data:
        return JSONResponse(content=[], status_code=200)

    return latest_data

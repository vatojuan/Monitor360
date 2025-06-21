from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.supabase_client import supabase

router = APIRouter()


# Esquema de respuesta para la API
class AlarmResponse(BaseModel):
    id: int
    client_id: Optional[int]
    severity: str
    message: str
    timestamp: datetime

    class Config:
        orm_mode = True


@router.get("/", response_model=List[AlarmResponse])
def get_all_alarms():
    try:
        response = (
            supabase.table("alarmas")
            .select("*")
            .order("timestamp", desc=True)
            .execute()
        )
        if response.error:
            raise HTTPException(status_code=500, detail=str(response.error))
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{alarm_id}", response_model=AlarmResponse)
def get_alarm_by_id(alarm_id: int):
    try:
        response = (
            supabase.table("alarmas").select("*").eq("id", alarm_id).single().execute()
        )
        if response.error:
            raise HTTPException(status_code=404, detail="Alarma no encontrada")
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

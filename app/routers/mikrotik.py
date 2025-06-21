from typing import List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.mikrotik_service import scan_mikrotiks

router = APIRouter()


class ScanRequest(BaseModel):
    ip_list: List[str]


@router.post("/mapa")
def scan_map(request: ScanRequest):
    """
    Escanea una lista de IPs de routers MikroTik y retorna el estado de cada uno.

    :param request.ip_list: Lista de direcciones IP a escanear.
    :return: Dict con IPs como clave y True (conectado) o False (error).
    """
    try:
        results = scan_mikrotiks(request.ip_list)
        return {"map": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al escanear MikroTik: {e}")

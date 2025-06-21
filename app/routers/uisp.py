from typing import Dict, List

from fastapi import APIRouter, HTTPException

from app.services.uisp_service import get_uisp_device_stats, get_uisp_devices

router = APIRouter()


@router.get("/", response_model=List[Dict])
def list_devices():
    """
    Lista todos los dispositivos registrados en UISP.
    :return: Lista de diccionarios con la información de cada dispositivo.
    """
    devices = get_uisp_devices()
    if devices is None:
        raise HTTPException(
            status_code=500, detail="Error obteniendo dispositivos de UISP"
        )
    return devices


@router.get("/{device_id}/stats", response_model=Dict)
def device_stats(device_id: str):
    """
    Obtiene estadísticas detalladas de un dispositivo específico de UISP.
    :param device_id: ID del dispositivo en UISP.
    :return: Diccionario con estadísticas del dispositivo.
    """
    stats = get_uisp_device_stats(device_id)
    if stats is None:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas de UISP para {device_id}",
        )
    return stats

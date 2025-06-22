#!/usr/bin/env python3
# File: app/routers/monitoring.py
import logging
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.mikrotik_service import scan_mikrotiks
from app.services.monitoring_service import monitor_and_store
from app.services.topology_enricher import get_enriched_topology
from app.services.trunk_service import get_trunk_topology
from app.services.uisp_service import get_uisp_devices

logger = logging.getLogger(__name__)
router = APIRouter()


# ──────────────────────────────────────────────
# Pydantic Schemas
# ──────────────────────────────────────────────


class StatusRequest(BaseModel):
    """Lista de routers MikroTik para verificar conectividad y UISP devices."""

    ip_list: List[str]


class RunRequest(BaseModel):
    """Routers de origen y clientes destino para test de capacidad."""

    router_ips: List[str]
    client_ips: List[str]


class TopologyRequest(BaseModel):
    """Lista de routers MikroTik semilla para descubrir topología."""

    ip_list: List[str]


# ──────────────────────────────────────────────
# Endpoints de Monitoreo
# ──────────────────────────────────────────────


@router.post("/status", response_model=Dict[str, Any], tags=["Estado"])
def get_full_status(request: StatusRequest):
    """
    Devuelve estado de conexión a MikroTik y lista de dispositivos UISP.
    """
    try:
        mikrotik_status = scan_mikrotiks(request.ip_list)
        uisp_devices = get_uisp_devices()
        return {"mikrotik": mikrotik_status, "uisp": uisp_devices}
    except Exception as e:
        logger.error("Error en /status", exc_info=e)
        raise HTTPException(status_code=500, detail=f"Error en status: {e}")


@router.post("/run", response_model=List[Dict[str, Any]], tags=["Test de capacidad"])
def run_monitor(request: RunRequest):
    """
    Ejecuta tests de capacidad, guarda mediciones y genera alarmas.
    """
    try:
        return monitor_and_store(request.router_ips, request.client_ips)
    except Exception as e:
        logger.error("Error en /run", exc_info=e)
        raise HTTPException(status_code=500, detail=f"Error ejecutando monitoreo: {e}")


@router.post("/topology", response_model=Dict[str, Any], tags=["Topología"])
def enriched_topology(request: TopologyRequest):
    """
    Genera la topología enriquecida (routers, switches, APs y clientes asociados).
    """
    try:
        return get_enriched_topology(request.ip_list)
    except Exception as e:
        # 📌 Aquí imprimimos el traceback completo para debug
        logger.error("Fallo en /topology", exc_info=e)
        # También podríamos usar traceback.print_exc()
        # traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generando topología: {e}")


@router.post("/trunk", response_model=Dict[str, Any], tags=["Topología Troncal"])
def trunk_topology(request: TopologyRequest):
    """
    Devuelve subgrafo de la red centrado en routers troncal y sus enlaces WAN.
    """
    try:
        return get_trunk_topology(request.ip_list)
    except Exception as e:
        logger.error("Error en /trunk", exc_info=e)
        raise HTTPException(
            status_code=500, detail=f"Error generando topología troncal: {e}"
        )

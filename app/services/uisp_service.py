# File: app/services/uisp_service.py
import logging
import os

import requests
import urllib3

# Suprimir warnings de certificados inseguros
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger(__name__)

# Config desde .env
UISP_URL = os.getenv("UISP_URL")  # ej. https://conecta360.uisp.com
UISP_LEGACY_TOKEN = os.getenv("UISP_LEGACY_TOKEN")

HEADERS = {"X-Auth-Token": UISP_LEGACY_TOKEN}


def get_uisp_devices() -> list:
    """
    Obtiene la lista de dispositivos UISP (sin verify para certificados self-signed).
    Retorna siempre una lista (o lista vacía en error).
    """
    try:
        url = f"{UISP_URL}/nms/api/v2.1/devices"
        logger.info(f"GET {url}")
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        # Algunos endpoints devuelven { data: […] }, otros directamente […]
        return data.get("data", data) if isinstance(data, dict) else data
    except Exception as e:
        logger.warning(f"Error al obtener dispositivos UISP: {e}")
        return []


def get_uisp_device_stats(device_id: str) -> dict:
    """
    Obtiene estadísticas detalladas de un dispositivo UCSIP por su ID.
    """
    try:
        url = f"{UISP_URL}/nms/api/v2.1/devices/{device_id}/statistics"
        logger.info(f"GET {url}")
        resp = requests.get(url, headers=HEADERS, timeout=10, verify=False)
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", {}) if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning(f"Error al obtener stats del dispositivo {device_id}: {e}")
        return {}

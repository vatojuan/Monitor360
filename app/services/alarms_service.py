import logging
from datetime import datetime, timezone
from typing import Optional

from app.supabase_client import supabase

logger = logging.getLogger(__name__)


def raise_alarm(severity: str, message: str, client_id: Optional[int] = None):
    """
    Registra una alarma en la tabla 'alarmas' de Supabase y escribe en los logs.
    """
    try:
        severity = severity.lower()
        if severity not in ("critical", "warning", "info"):
            raise ValueError(f"Severidad inválida: {severity}")

        data = {
            "client_id": client_id if client_id is not None else None,
            "severity": severity,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        response = supabase.table("alarmas").insert(data).execute()

        if response.get("status_code") not in [200, 201]:
            logger.warning(f"No se pudo guardar alarma en Supabase: {response}")
        else:
            logger.warning(f"🚨 [{severity.upper()}] {message}")

    except Exception as e:
        logger.error(f"Error al guardar alarma en Supabase: {e}")

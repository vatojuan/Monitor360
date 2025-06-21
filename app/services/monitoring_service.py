# File: app/services/monitoring_service.py
"""Monitorea capacidad/estado de clientes y persiste resultados en Supabase.
   ▸ Ejecuta `traffic‑generator` desde MikroTik a cada cliente.
   ▸ Consulta señal desde UISP (si existe).
   ▸ Guarda/actualiza registro de cliente en tabla `topologia`.
   ▸ Genera alarma en Supabase vía `raise_alarm` cuando se superan umbrales.
"""

import logging
import os
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from dotenv import load_dotenv

from app.services.alarms_service import raise_alarm
from app.services.mikrotik_service import connect_mikrotik_with_learning
from app.services.uisp_service import get_uisp_device_stats, get_uisp_devices
from app.supabase_client import supabase

# ──────────────────────────────────────────────
# Configuración y logger
# ──────────────────────────────────────────────
env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
load_dotenv(env_path)

THRESHOLD_LOSS = float(os.getenv("THRESHOLD_LOSS_PERCENT", "15"))
THRESHOLD_SIGNAL = float(os.getenv("THRESHOLD_SIGNAL_DBM", "-75"))
THRESHOLD_CAPACITY = float(os.getenv("THRESHOLD_CAPACITY_MBPS", "15"))
TEST_RATE = os.getenv("TEST_RATE", "10M")  # "10M", "50M", etc.
TEST_DURATION = int(os.getenv("TEST_DURATION", "10"))  # segundos

log_file = os.getenv("LOG_FILE", "monitor360.log")
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────


def _parse_rate(rate_str: str) -> float:
    """Convierte '10M' o '25Mbps' → 10.0 / 25.0 (Mbps)."""
    if not rate_str:
        return 0.0
    num = "".join(c for c in rate_str if (c.isdigit() or c == "."))
    try:
        return float(num)
    except ValueError:
        return 0.0


def _run_capacity_test(router_ip: str, client_ip: str) -> Dict[str, Any]:
    """Lanza traffic‑generator UDP desde router → cliente y devuelve pérdida/tx_rate."""
    api = connect_mikrotik_with_learning(router_ip)
    if api is None:
        raise RuntimeError(f"No se pudo conectar a MikroTik {router_ip}")

    tg = api.get_resource("/tool/traffic-generator")
    test_name = f"tg_{client_ip.replace('.', '_')}"

    # Crear prueba
    tg.add(
        name=test_name,
        protocol="udp",
        src_address=router_ip,
        dst_address=client_ip,
        packet_size="1500",
        rate=TEST_RATE,
        duration=str(TEST_DURATION),
    )

    # Iniciar
    api.get_binary_resource("/tool/traffic-generator").call(
        "start", {"numbers": test_name}
    )
    logger.info(
        f"▶️ [{router_ip}] → {client_ip} | rate={TEST_RATE} dur={TEST_DURATION}s"
    )

    time.sleep(TEST_DURATION + 1)

    # Leer resultado
    for entry in tg.get():
        if entry.get("name") == test_name:
            return {
                "tx_rate": _parse_rate(entry.get("tx-rate")),  # Mbps
                "loss": float(entry.get("loss", 100)),  # %
            }

    return {"tx_rate": 0.0, "loss": 100.0}


# ──────────────────────────────────────────────
# Core
# ──────────────────────────────────────────────


def monitor_and_store(
    router_ips: List[str], client_ips: List[str]
) -> List[Dict[str, Any]]:
    """Ejecuta pruebas a cada <router_ip, client_ip> y guarda en Supabase."""
    results: List[Dict[str, Any]] = []

    # Cache de dispositivos UISP para señales
    dev_cache = get_uisp_devices()
    ip_to_uisp = {dev["ipAddress"]: dev for dev in dev_cache if dev.get("ipAddress")}

    for router_ip in router_ips:
        for client_ip in client_ips:
            try:
                cap = _run_capacity_test(router_ip, client_ip)

                # Datos UISP si existe
                uisp_stats = {}
                if client_ip in ip_to_uisp:
                    uisp_stats = get_uisp_device_stats(ip_to_uisp[client_ip]["id"])

                # Upsert en tabla topologia
                supabase.table("topologia").upsert(
                    {
                        "ip": client_ip,
                        "tipo": "measurement",
                        "nombre": ip_to_uisp.get(client_ip, {})
                        .get("identification", {})
                        .get("name", client_ip),
                        "signal": uisp_stats.get("rssi"),
                        "velocidad_link": f"{cap['tx_rate']}Mbps",
                        "last_seen": datetime.now(timezone.utc).isoformat(),
                    }
                ).execute()

                # Alarmas
                if cap["loss"] > THRESHOLD_LOSS:
                    raise_alarm(
                        "critical",
                        f"{client_ip}: pérdida {cap['loss']}% > {THRESHOLD_LOSS}%",
                    )
                if cap["tx_rate"] < THRESHOLD_CAPACITY:
                    raise_alarm(
                        "warning",
                        f"{client_ip}: capacidad {cap['tx_rate']} Mbps < {THRESHOLD_CAPACITY} Mbps",
                    )
                if (
                    uisp_stats.get("rssi") is not None
                    and uisp_stats["rssi"] < THRESHOLD_SIGNAL
                ):
                    raise_alarm(
                        "warning",
                        f"{client_ip}: señal {uisp_stats['rssi']} dBm < {THRESHOLD_SIGNAL} dBm",
                    )

                results.append(
                    {
                        "client": client_ip,
                        "capacity": cap,
                        "signal": uisp_stats.get("rssi"),
                    }
                )
            except Exception as exc:
                logger.error(
                    f"❌ Error monitoreando {client_ip} via {router_ip}: {exc}"
                )

    return results

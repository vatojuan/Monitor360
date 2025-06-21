#!/usr/bin/env python3
"""
Script profesional para verificar correspondencia entre clientes de CSV y dispositivos UISP.
Genera reportes en JSON y CSV para un análisis detallado.
"""

import argparse
import csv
import json
import logging
import os
import sys
from datetime import datetime

# Asegurar que podamos importar el paquete 'app' desde la raíz del proyecto
dir_path = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(dir_path, "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.services.client_service import load_clients_csv  # noqa: E402
from app.services.uisp_service import get_uisp_devices  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(message)s")


def build_indices(devices):
    """
    Construye índices por IP, MAC y nombre para búsqueda rápida.
    """
    idx_ip, idx_mac, idx_name = {}, {}, {}

    for dev in devices:
        ip = dev.get("ipAddress", "")
        mac = dev.get("mac") or dev.get("identification", {}).get("mac")
        name = dev.get("identification", {}).get("name")

        if ip:
            idx_ip[ip] = dev
        if mac:
            idx_mac[mac.lower()] = dev
        if name:
            idx_name[name.lower()] = dev
    return idx_ip, idx_mac, idx_name


def verify(csv_path, out_dir):
    """
    Ejecuta la verificación, genera reportes en out_dir.
    """
    logger.info(f"Cargando clientes desde CSV: {csv_path}")
    clients = load_clients_csv(csv_path)

    logger.info("Obteniendo dispositivos UISP...")
    devices = get_uisp_devices()
    logger.info(f"Dispositivos UISP obtenidos: {len(devices)}")

    idx_ip, idx_mac, idx_name = build_indices(devices)

    resumen = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "total_clients": len(clients),
        "matched": 0,
        "unmatched": 0,
    }
    detalle = []
    sin_match = []

    for _, row in clients.iterrows():
        client_ip = str(row.get("Ip") or row.get("ip") or "").strip()
        client_mac = str(row.get("Mac") or row.get("mac") or "").strip().lower()
        client_name = str(row.get("Nombre") or row.get("nombre") or "").strip().lower()

        match = None
        método = None

        # 1. Por IP
        if client_ip and client_ip in idx_ip:
            match = idx_ip[client_ip]
            método = "ip"
        # 2. Por MAC
        elif client_mac and client_mac in idx_mac:
            match = idx_mac[client_mac]
            método = "mac"
        # 3. Por nombre exacto
        elif client_name and client_name in idx_name:
            match = idx_name[client_name]
            método = "name"

        entry = {
            "cliente_id": row.get("Id"),
            "cliente_nombre": row.get("Nombre"),
            "cliente_ip": client_ip,
            "cliente_mac": client_mac,
        }
        if match:
            resumen["matched"] += 1
            entry.update(
                {
                    "matched": True,
                    "método": método,
                    "uisp_id": match.get("identification", {}).get("id"),
                    "uisp_name": match.get("identification", {}).get("name"),
                    "uisp_ip": match.get("ipAddress"),
                    "uisp_mac": match.get("mac")
                    or match.get("identification", {}).get("mac"),
                }
            )
        else:
            resumen["unmatched"] += 1
            entry["matched"] = False
            sin_match.append(entry)

        detalle.append(entry)

    # Escribir reportes
    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, "resumen_uisp_vs_clients.json")
    with open(json_path, "w", encoding="utf-8") as jf:
        json.dump(resumen, jf, indent=2, ensure_ascii=False)
    logger.info(f"Resumen guardado en {json_path}")

    csv_path = os.path.join(out_dir, "detalle_uisp_vs_clients.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
        writer = csv.DictWriter(cf, fieldnames=list(detalle[0].keys()))
        writer.writeheader()
        writer.writerows(detalle)
    logger.info(f"Detalle guardado en {csv_path}")

    sin_path = os.path.join(out_dir, "clientes_sin_match.json")
    with open(sin_path, "w", encoding="utf-8") as sf:
        json.dump(sin_match, sf, indent=2, ensure_ascii=False)
    logger.info(f"Clientes sin match guardados en {sin_path}")

    logger.info("¡Verificación completada!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Verifica correspondencia CSV ↔ UISP y genera reportes en JSON/CSV"
    )
    parser.add_argument("--csv", required=True, help="Ruta al CSV de clientes")
    parser.add_argument(
        "--out", default="reports", help="Carpeta de salida para reportes"
    )
    args = parser.parse_args()

    verify(args.csv, args.out)

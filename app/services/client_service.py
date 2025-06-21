"""
Servicio de clientes: carga CSV y asocia a dispositivos UISP.
"""

import os
from typing import Dict, List, Optional

import pandas as pd

# Ruta por defecto al CSV de clientes (puedes ajustar en .env)
CLIENT_CSV_PATH = os.getenv("CLIENT_CSV_PATH", "Lista de Usuarios.csv")


def load_clients_csv(file_path: Optional[str] = None) -> pd.DataFrame:
    """
    Carga el CSV de clientes exportado de MikroWisp.

    - Normaliza nombres de columnas a minúsculas y sin espacios.
    - Devuelve un DataFrame de pandas.
    """
    path = file_path or CLIENT_CSV_PATH
    df = pd.read_csv(path, sep=",", dtype=str)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def associate_clients_to_devices(
    client_df: pd.DataFrame, uisp_devices: List[Dict]
) -> List[Dict]:
    """
    Asocia cada cliente del DataFrame con un dispositivo UISP.

    Estrategia:
      1. Mapeo IP exacta: si coincide, se asocia.
      2. (En futuras versiones: heurísticas /24, difflib, etc.)

    Retorna lista de dicts con:
      - cliente_nombre
      - plan
      - ip
      - dispositivo_id
      - mac
      - hostname
    """
    asociaciones: List[Dict] = []
    # Construir mapa ip → dispositivo
    ip_map = {dev.get("ipAddress"): dev for dev in uisp_devices if dev.get("ipAddress")}

    for _, row in client_df.iterrows():
        raw_ip = row.get("ip")
        if pd.isna(raw_ip) or not raw_ip:
            continue
        client_ip = str(raw_ip).strip()
        dev = ip_map.get(client_ip)
        if not dev:
            continue

        identification = dev.get("identification") or {}
        asociaciones.append(
            {
                "cliente_nombre": str(row.get("nombre") or "").strip(),
                "plan": str(row.get("plan") or "").strip(),
                "ip": client_ip,
                "dispositivo_id": identification.get("id"),
                "mac": identification.get("mac"),
                "hostname": identification.get("hostname"),
            }
        )

    return asociaciones


__all__ = [
    "load_clients_csv",
    "associate_clients_to_devices",
]

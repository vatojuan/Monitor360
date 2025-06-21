"""
Servicio de clientes: carga CSV y asocia a dispositivos UISP.

Incluye heurística avanzada:
  1. IP exacta
  2. MAC exacta
  3. Nombre exacto
  4. IP misma subred /24
  5. Nombre similar (difflib)
"""

import ipaddress
import os
from difflib import SequenceMatcher
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
    client_df: pd.DataFrame, uisp_devices: List[Dict], fuzzy_threshold: float = 0.8
) -> List[Dict]:
    """
    Asocia cada cliente del DataFrame con un dispositivo UISP.

    Retorna lista de dicts con:
      - cliente_nombre
      - plan (si existe en CSV)
      - ip
      - cliente_mac
      - matched (bool)
      - método de matching
      - similarity (solo para fuzzy)
      - dispositivo_id, hostname, uisp_ip, uisp_mac si matched
    """
    asociaciones: List[Dict] = []
    # Mapas para búsqueda rápida
    ip_map = {dev.get("ipAddress"): dev for dev in uisp_devices if dev.get("ipAddress")}
    mac_map = {
        (dev.get("mac") or dev.get("identification", {}).get("mac", "")).lower(): dev
        for dev in uisp_devices
    }
    name_map = {
        dev.get("identification", {}).get("name", "").lower(): dev
        for dev in uisp_devices
        if dev.get("identification", {}).get("name")
    }

    for _, row in client_df.iterrows():
        client_ip = str(row.get("ip") or row.get("ip_address") or "").strip()
        client_mac = str(row.get("mac") or "").strip().lower()
        client_name = str(row.get("nombre") or row.get("name") or "").strip().lower()

        match = None
        method = None
        similarity = None

        # 1. IP exacta
        if client_ip and client_ip in ip_map:
            match = ip_map[client_ip]
            method = "ip_exact"
        # 2. MAC exacta
        elif client_mac and client_mac in mac_map:
            match = mac_map[client_mac]
            method = "mac_exact"
        # 3. Nombre exacto
        elif client_name and client_name in name_map:
            match = name_map[client_name]
            method = "name_exact"
        # 4. Misma subred /24
        elif client_ip:
            try:
                net = ipaddress.ip_network(client_ip + "/24", strict=False)
                for ip_addr, dev in ip_map.items():
                    if ipaddress.ip_address(ip_addr) in net:
                        match = dev
                        method = "subnet_24"
                        break
            except ValueError:
                pass
        # 5. Nombre similar (fuzzy)
        if not match and client_name:
            best_ratio = 0.0
            best_dev = None
            for name_key, dev in name_map.items():
                ratio = SequenceMatcher(None, client_name, name_key).ratio()
                if ratio > best_ratio:
                    best_ratio, best_dev = ratio, dev
            if best_ratio >= fuzzy_threshold:
                match = best_dev
                method = "name_fuzzy"
                similarity = round(best_ratio, 2)

        # Construir entry de salida
        entry: Dict = {
            "cliente_nombre": str(row.get("nombre") or row.get("name") or "").strip(),
            "plan": str(row.get("plan") or "").strip(),
            "ip": client_ip,
            "cliente_mac": client_mac,
            "matched": bool(match),
            "método": method,
        }
        if similarity is not None:
            entry["similarity"] = similarity
        if match:
            identification = match.get("identification", {})
            entry.update(
                {
                    "dispositivo_id": identification.get("id"),
                    "hostname": identification.get("hostname"),
                    "uisp_ip": match.get("ipAddress"),
                    "uisp_mac": match.get("mac") or identification.get("mac"),
                }
            )

        asociaciones.append(entry)

    return asociaciones


__all__ = [
    "load_clients_csv",
    "associate_clients_to_devices",
]

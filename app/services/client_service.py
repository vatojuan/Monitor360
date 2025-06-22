"""
Servicio de clientes: carga CSV y asocia a dispositivos UISP.

Incluye heurística avanzada:
  1. IP exacta
  2. MAC exacta
  3. Nombre exacto (case-sensitive)
  4. IP misma subred /24
  5. Nombre similar (fuzzy)
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
      - plan (si existe)
      - ip
      - cliente_mac
      - matched (bool)
      - método (ip_exact, mac_exact, name_exact, subnet_24, name_fuzzy)
      - similarity (solo para name_fuzzy)
      - dispositivo_id, hostname, uisp_ip, uisp_mac, uisp_name si matched
    """
    asociaciones: List[Dict] = []
    # Mapas de acceso rápido
    ip_map = {dev.get("ipAddress"): dev for dev in uisp_devices if dev.get("ipAddress")}
    mac_map = {}
    for dev in uisp_devices:
        mac = (dev.get("mac") or dev.get("identification", {}).get("mac", "")).lower()
        if mac:
            mac_map[mac] = dev

    for _, row in client_df.iterrows():
        client_ip = str(row.get("ip") or row.get("ip_address") or "").strip()
        client_mac = str(row.get("mac") or "").strip().lower()
        client_name_raw = str(row.get("nombre") or row.get("name") or "").strip()
        client_name = client_name_raw
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
        # 3. Nombre exacto (case-sensitive)
        elif client_name:
            for dev in uisp_devices:
                dev_name = dev.get("identification", {}).get("name")
                if dev_name and dev_name == client_name:
                    match = dev
                    method = "name_exact"
                    break
        # 4. Misma subred /24
        if not match and client_ip:
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
            for dev in uisp_devices:
                dev_name = dev.get("identification", {}).get("name")
                if dev_name:
                    ratio = SequenceMatcher(
                        None, client_name.lower(), dev_name.lower()
                    ).ratio()
                    if ratio > best_ratio:
                        best_ratio = ratio
                        best_dev = dev
            if best_ratio >= fuzzy_threshold and best_dev:
                match = best_dev
                method = "name_fuzzy"
                similarity = round(best_ratio, 2)

        entry: Dict = {
            "cliente_nombre": client_name,
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
                    "uisp_name": identification.get("name"),
                }
            )

        asociaciones.append(entry)

    return asociaciones


__all__ = [
    "load_clients_csv",
    "associate_clients_to_devices",
]

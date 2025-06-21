# File: app/services/associate_clients.py

from typing import Dict, List

import pandas as pd


def load_clients_csv(file_path: str = "Lista de Usuarios.csv") -> pd.DataFrame:
    """
    Carga y normaliza el CSV exportado desde MikroWisp.
    """
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.lower().str.strip()  # Normaliza nombres de columnas
    return df


def associate_clients_to_devices(
    client_df: pd.DataFrame, uisp_devices: List[Dict]
) -> List[Dict]:
    """
    Asocia clientes del CSV con dispositivos de UISP.
    Primero intenta por IP exacta (ip_address), luego por coincidencia de nombre.
    Retorna una lista de asociaciones con datos útiles.
    """
    asociaciones = []

    # Preprocesar dispositivos UISP: mapa de ipAddress a device
    ip_map = {dev.get("ipAddress"): dev for dev in uisp_devices if dev.get("ipAddress")}

    for _, row in client_df.iterrows():
        client_ip = str(row.get("ip", "") or "").strip()
        client_name = str(row.get("nombre", "") or "").strip()
        matched = None

        # 1. Intentar asociación por IP exacta
        if client_ip and client_ip in ip_map:
            matched = ip_map[client_ip]
        else:
            # 2. Intentar asociación por nombre substring
            for device in uisp_devices:
                identification = device.get("identification") or {}
                dev_name = str(identification.get("name") or "").strip()
                if client_name and client_name.lower() in dev_name.lower():
                    matched = device
                    break

        if matched:
            identification = matched.get("identification") or {}
            asociaciones.append(
                {
                    "cliente_id": row.get("cliente_id"),
                    "nombre": client_name,
                    "plan": row.get("plan", ""),
                    "ip": client_ip,
                    "dispositivo_id": identification.get("id", ""),
                    "mac": identification.get("mac", ""),
                    "hostname": identification.get("hostname", ""),
                }
            )

    return asociaciones

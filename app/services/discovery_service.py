# File: app/services/discovery_service.py

import logging
from collections import deque
from datetime import datetime, timezone
from typing import Dict, List, Set

from app.services.alarms_service import raise_alarm
from app.services.mikrotik_service import connect_mikrotik_with_learning
from app.services.uisp_service import get_uisp_devices
from app.supabase_client import supabase

logger = logging.getLogger(__name__)

# Tipos de nodos en el grafo
NODE_ROUTER = "router"
NODE_CLIENT = "client"
NODE_AP = "ap"
NODE_SWITCH = "switch"

# Umbral para detectar degradación de enlace (10 Mbps)
DEGRADED_SPEEDS = {"10Mbps", "10M"}  # ampliar si es necesario


def _interface_details(api) -> List[Dict]:
    """Lista de interfaces Ethernet con info de link-speed y degradación."""
    details = []
    try:
        eth = api.get_resource("/interface/ethernet").get()
        for inf in eth:
            details.append(
                {
                    "name": inf.get("name"),
                    "running": inf.get("running") == "true",
                    "link_speed": inf.get("link-speed"),
                    "degraded": inf.get("link-speed") in DEGRADED_SPEEDS,
                }
            )
    except Exception as e:
        logger.warning(f"No se pudieron obtener interfaces Ethernet: {e}")
    return details


def _discover_clients_from_router(api) -> Set[str]:
    """IP de clientes desde queues y tabla ARP."""
    client_ips: Set[str] = set()
    try:
        queues = api.get_resource("/queue/simple").get()
        for q in queues:
            target = q.get("target")
            if target and target != "0.0.0.0/0":
                for part in target.split(","):
                    ip = part.split("/")[0]
                    client_ips.add(ip)
    except Exception as e:
        logger.warning(f"No se pudieron leer queues: {e}")
    try:
        arp = api.get_resource("/ip/arp").get()
        for entry in arp:
            if entry.get("address"):
                client_ips.add(entry["address"])
    except Exception as e:
        logger.warning(f"No se pudieron leer tabla ARP: {e}")
    return {ip for ip in client_ips if ip}


def _discover_switch_neighbors(api) -> List[Dict]:
    """Vecinos LLDP/CDP desde /ip neighbor."""
    neighbors = []
    try:
        neigh = api.get_resource("/ip/neighbor").get()
        for n in neigh:
            if n.get("address"):
                neighbors.append(
                    {
                        "address": n["address"],
                        "identity": n.get("identity"),
                        "interface": n.get("interface"),
                    }
                )
    except Exception as e:
        logger.warning(f"No se pudo obtener vecinos: {e}")
    return neighbors


def discover_topology(seed_router_ips: List[str]) -> Dict:
    """Construye el grafo partiendo de routers semilla e inserta nodos en Supabase."""
    nodes: List[Dict] = []
    edges: List[Dict] = []

    visited: Set[str] = set()
    queue = deque(seed_router_ips)

    # Obtener dispositivos UISP para correlación
    uisp_devices = get_uisp_devices()
    ip_to_uisp = {d.get("ipAddress"): d for d in uisp_devices if d.get("ipAddress")}

    while queue:
        ip = queue.popleft()
        if ip in visited:
            continue
        visited.add(ip)

        api = connect_mikrotik_with_learning(ip)
        router_status = api is not None
        nodes.append(
            {"id": ip, "label": ip, "type": NODE_ROUTER, "status": router_status}
        )
        supabase.table("topologia").upsert(
            {
                "ip": ip,
                "tipo": NODE_ROUTER,
                "nombre": ip,
                "last_seen": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()

        if not router_status:
            continue

        # Interfaces Ethernet y degradación
        for inf in _interface_details(api):
            if inf["running"] and inf["degraded"]:
                port_id = f"{ip}:{inf['name']}"
                nodes.append(
                    {
                        "id": port_id,
                        "label": f"{inf['name']} ({inf['link_speed']})",
                        "type": NODE_SWITCH,
                        "degraded": True,
                        "link_speed": inf["link_speed"],
                    }
                )
                edges.append(
                    {
                        "source": ip,
                        "target": port_id,
                        "degraded": True,
                        "link_speed": inf["link_speed"],
                    }
                )
                raise_alarm(
                    "warning",
                    f"Enlace degradado a {inf['link_speed']} en {ip} interfaz {inf['name']}",
                )
                supabase.table("topologia").upsert(
                    {
                        "ip": ip,
                        "tipo": NODE_SWITCH,
                        "nombre": inf["name"],
                        "puerto": inf["name"],
                        "velocidad_link": inf["link_speed"],
                        "last_seen": datetime.now(timezone.utc).isoformat(),
                    }
                ).execute()

        # Vecinos LLDP/CDP
        for neigh in _discover_switch_neighbors(api):
            neighbor_ip = neigh["address"]
            if neighbor_ip not in [n["id"] for n in nodes]:
                nodes.append(
                    {
                        "id": neighbor_ip,
                        "label": neigh["identity"] or neighbor_ip,
                        "type": NODE_SWITCH,
                    }
                )
                supabase.table("topologia").upsert(
                    {
                        "ip": neighbor_ip,
                        "tipo": NODE_SWITCH,
                        "nombre": neigh.get("identity") or neighbor_ip,
                        "last_seen": datetime.now(timezone.utc).isoformat(),
                    }
                ).execute()
            edges.append(
                {"source": ip, "target": neighbor_ip, "puerto": neigh["interface"]}
            )

        # Clientes desde MikroTik + UISP
        for c_ip in _discover_clients_from_router(api):
            if c_ip not in [n["id"] for n in nodes]:
                dev = ip_to_uisp.get(c_ip)
                nodes.append(
                    {
                        "id": c_ip,
                        "label": dev["identification"]["name"] if dev else c_ip,
                        "type": NODE_CLIENT,
                        "signal": dev.get("rssi") if dev else None,
                    }
                )
                supabase.table("topologia").upsert(
                    {
                        "ip": c_ip,
                        "tipo": NODE_CLIENT,
                        "nombre": dev["identification"]["name"] if dev else c_ip,
                        "signal": dev.get("rssi") if dev else None,
                        "last_seen": datetime.now(timezone.utc).isoformat(),
                    }
                ).execute()
            edges.append({"source": ip, "target": c_ip})

    # Relaciones AP-cliente desde UISP
    for dev in uisp_devices:
        if dev.get("parentId"):
            parent = next((d for d in uisp_devices if d["id"] == dev["parentId"]), None)
            if parent:
                child_ip = dev.get("ipAddress")
                parent_ip = parent.get("ipAddress")
                if child_ip and parent_ip:
                    edges.append({"source": parent_ip, "target": child_ip})
                    nodes.append(
                        {
                            "id": parent_ip,
                            "label": parent["identification"]["name"],
                            "type": NODE_AP,
                        }
                    )
                    supabase.table("topologia").upsert(
                        {
                            "ip": parent_ip,
                            "tipo": NODE_AP,
                            "nombre": parent["identification"]["name"],
                            "last_seen": datetime.now(timezone.utc).isoformat(),
                        }
                    ).execute()

    return {"nodes": nodes, "edges": edges}

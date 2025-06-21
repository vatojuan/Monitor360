# File: app/services/trunk_service.py
import logging
from collections import deque
from typing import Any, Dict, List

from app.services.mikrotik_service import connect_mikrotik_with_learning

logger = logging.getLogger(__name__)

# Define tipo de nodo
NODE_ROUTER = "router"


def get_trunk_topology(seed_router_ips: List[str]) -> Dict[str, Any]:
    """
    Genera un subgrafo centrado en los routers troncal y sus enlaces WAN entre ellos.
    Solo incluye nodos y conexiones directas L2 entre routers de la lista.
    """
    nodes = []
    edges = []
    visited = set()
    queue = deque(seed_router_ips)

    while queue:
        ip = queue.popleft()
        if ip in visited:
            continue
        visited.add(ip)

        api = connect_mikrotik_with_learning(ip)
        status = api is not None
        nodes.append(
            {
                "id": ip,
                "label": ip,
                "type": NODE_ROUTER,
                "status": status,
            }
        )
        if not status:
            continue

        # Vecinos L2 por LLDP/CDP
        try:
            neigh = api.get_resource("/ip/neighbor").get()
            for n in neigh:
                nbr_ip = n.get("address")
                if nbr_ip in seed_router_ips:
                    # Añadir arista solo entre routers semilla
                    edges.append(
                        {
                            "source": ip,
                            "target": nbr_ip,
                            "interface": n.get("interface"),
                        }
                    )
        except Exception as e:
            logger.warning(f"Error al obtener vecinos L2 en {ip}: {e}")

    return {"nodes": nodes, "edges": edges}

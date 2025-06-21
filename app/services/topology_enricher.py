# File: app/services/topology_enricher.py
import json
import logging
import os
from typing import Dict, List, Optional

from app.services.client_service import associate_clients_to_devices, load_clients_csv
from app.services.discovery_service import discover_topology
from app.services.uisp_service import get_uisp_devices

logger = logging.getLogger(__name__)


def get_enriched_topology(
    seed_router_ips: List[str], clients_csv_path: Optional[str] = None
) -> Dict:
    """
    Genera topología enriquecida uniendo:
    - Descubrimiento de red (routers, switches, clientes).
    - Asociaciones de clientes desde CSV + UISP.

    Guarda el JSON enriquecido en 'topology_enriched.json'.
    """
    # 1. Descubre la topología pura
    topology = discover_topology(seed_router_ips)

    # 2. Carga clientes y dispositivos UISP
    client_df = load_clients_csv(clients_csv_path)
    uisp_devices = get_uisp_devices()

    # 3. Asocia clientes a dispositivos UISP
    associations = associate_clients_to_devices(client_df, uisp_devices)
    assoc_map = {a["ip"]: a for a in associations}

    # 4. Enriquecer nodos de tipo 'client'
    enriched_nodes: List[Dict] = []
    for node in topology.get("nodes", []):
        if node.get("type") == "client":
            assoc = assoc_map.get(node.get("id"))
            if assoc:
                node.update(assoc)
        enriched_nodes.append(node)
    topology["nodes"] = enriched_nodes

    # 5. Guardar JSON enriquecido
    output = os.getenv("ENRICHED_OUTPUT", "topology_enriched.json")
    with open(output, "w") as f:
        json.dump(topology, f, indent=2)
    logger.info(f"Topology enriched saved to {output}")
    return topology

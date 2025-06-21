# File: app/routers/topologia.py
from typing import List

from fastapi import APIRouter, Query

from app.services.topology_enricher import get_enriched_topology

router = APIRouter()


@router.get("/topologia/full")
def obtener_topologia(
    seed_ips: List[str] = Query(["10.0.0.1", "10.0.0.2"]),
    clients_csv: str = "clientes.csv",
):
    """
    Devuelve la topología completa y enriquecida desde MikroTik, UISP y CSV
    """
    topologia = get_enriched_topology(seed_ips, clients_csv)
    return topologia

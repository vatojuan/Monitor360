import json

from app.services.topology_enricher import get_enriched_topology

if __name__ == "__main__":
    # Routers troncales (WAN y clientes)
    seeds = ["45.172.141.122", "45.172.141.35"]
    enriched = get_enriched_topology(seeds)

    # Guarda JSON para frontend
    with open("topology_enriched.json", "w", encoding="utf-8") as f:
        json.dump(enriched, f, ensure_ascii=False, indent=2)

    print("✅ topology_enriched.json generado con nodos enriquecidos.")

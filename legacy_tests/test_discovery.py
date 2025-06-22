# test_discovery.py
from app.services.discovery import discover_network_topology

if __name__ == "__main__":
    result = discover_network_topology()

    print("\n=== INTERFACES MIKROTIK ===")
    for t in result["mikrotik_trunks"]:
        print(f"- {t['name']} ({t['type']}), MAC: {t.get('mac_address')}")

    print("\n=== DISPOSITIVOS UISP ===")
    for d in result["uisp_devices"][:10]:  # Solo los primeros 10
        print(f"- {d.get('identification', {}).get('name')}")

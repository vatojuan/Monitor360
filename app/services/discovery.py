import logging

from app.services.uisp_service import get_uisp_devices
from app.utils.mikrotik_connect import connect_to_mikrotik

logger = logging.getLogger("discovery")


def get_mikrotik_trunks(api) -> list:
    """Devuelve interfaces activas que podrían considerarse troncales."""
    try:
        interfaces = api.get_resource("/interface").get()
        trunks = [
            {
                "name": iface["name"],
                "type": iface.get("type", "ether"),
                "running": iface.get("running"),
                "mac_address": iface.get("mac-address"),
            }
            for iface in interfaces
            if iface.get("running") == "true"
        ]
        return trunks
    except Exception as e:
        logger.warning(f"Error al obtener interfaces MikroTik: {e}")
        return []


def discover_network_topology():
    logger.info("🔍 Descubriendo topología de red...")

    # MikroTik
    api = connect_to_mikrotik()
    mikrotik_trunks = get_mikrotik_trunks(api)
    logger.info(
        f"  ✅ MikroTik: {len(mikrotik_trunks)} interfaces activas encontradas."
    )

    # UISP
    uisp_devices = get_uisp_devices()
    logger.info(f"  ✅ UISP: {len(uisp_devices)} dispositivos encontrados.")

    return {"mikrotik_trunks": mikrotik_trunks, "uisp_devices": uisp_devices}

import json
import logging
import os

from dotenv import load_dotenv
from routeros_api import RouterOsApiPool

# Cargar variables de entorno
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", ".env")
load_dotenv(env_path)

# Parámetros de configuración
PASSWORDS = json.loads(os.getenv("MIKROTIK_COMMON_PASSWORDS", "[]"))
PORT = int(os.getenv("MIKROTIK_PORT", 8728))
TIMEOUT = int(os.getenv("MIKROTIK_TIMEOUT", 5))
CREDENTIALS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "mikrotik_credentials.json"
)
LOG_FILE = os.getenv("LOG_FILE", "monitor360.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Configurar logging
logging.basicConfig(
    filename=LOG_FILE,
    filemode="a",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)


def load_known_credentials() -> dict:
    """
    Carga las credenciales conocidas de MikroTik (IP -> password) desde un archivo JSON.
    """
    try:
        if os.path.exists(CREDENTIALS_FILE):
            with open(CREDENTIALS_FILE, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.warning(f"No se pudo leer el archivo de credenciales: {e}")
    return {}


def save_known_credentials(creds: dict):
    """
    Guarda las credenciales conocidas de MikroTik en un archivo JSON.
    """
    try:
        with open(CREDENTIALS_FILE, "w") as f:
            json.dump(creds, f, indent=2)
        logger.debug("Credenciales guardadas exitosamente.")
    except Exception as e:
        logger.error(f"Error al guardar credenciales: {e}")


def connect_mikrotik_with_learning(ip: str) -> RouterOsApiPool | None:
    """
    Intenta conectarse a un MikroTik usando el usuario 'admin' y una lista de contraseñas.
    Si una contraseña funciona, la guarda para futuros intentos.

    :param ip: Dirección IP del router MikroTik.
    :return: Instancia de API de RouterOS si la conexión es exitosa, None en caso de fallo.
    """
    known = load_known_credentials()
    passwords_to_try = []

    # Priorizar contraseña conocida
    if ip in known:
        passwords_to_try.append(known[ip])

    # Agregar contraseñas comunes
    for pwd in PASSWORDS:
        if pwd not in passwords_to_try:
            passwords_to_try.append(pwd)

    # Intentar conectarse con cada contraseña
    for password in passwords_to_try:
        try:
            api_pool = RouterOsApiPool(
                host=ip,
                username="admin",
                password=password,
                port=PORT,
                plaintext_login=True,
                timeout=TIMEOUT,
            )
            api = api_pool.get_api()
            logger.info(f"Conexión exitosa a {ip} con contraseña '{password}'")

            # Guardar la contraseña exitosa
            known[ip] = password
            save_known_credentials(known)

            return api
        except Exception as e:
            logger.warning(f"Fallo conexión a {ip} con '{password}': {e}")

    # Si ninguna contraseña funcionó
    logger.error(f"No se pudo conectar a {ip} con ninguna contraseña conocida.")
    return None


def scan_mikrotiks(ip_list: list[str]) -> dict[str, bool]:
    """
    Escanea una lista de IPs de MikroTik e intenta conectarse a cada una.

    :param ip_list: Lista de IPs a escanear.
    :return: Diccionario {ip: True si conexión exitosa, False en caso contrario}.
    """
    results = {}
    for ip in ip_list:
        api = connect_mikrotik_with_learning(ip)
        results[ip] = api is not None
    return results

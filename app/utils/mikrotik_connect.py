import os

from routeros_api import RouterOsApiPool


def connect_to_mikrotik():
    host = os.getenv("MIKROTIK_HOST")
    user = os.getenv("MIKROTIK_USER", "admin")
    password = os.getenv("MIKROTIK_PASSWORDS", "").split(",")[0].strip()
    port = int(os.getenv("MIKROTIK_PORT", "8728"))

    if not host or not password:
        raise ValueError("Faltan variables de entorno para MikroTik")

    connection = RouterOsApiPool(
        host,
        username=user,
        password=password,
        port=port,
        use_ssl=False,
        plaintext_login=True,
    )
    return connection.get_api()

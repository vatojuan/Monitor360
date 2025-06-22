# File: test_api.py
import os
import time

import requests

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/monitoring")


def pretty(resp):
    print(f"→ {resp.status_code} {resp.reason}")
    try:
        print(resp.json())
    except Exception as e:
        # Capturamos solo excepciones estándar, no todo
        print(f"Error parsing JSON: {e}")
        print(resp.text)
    print("-" * 60)


def main():
    # 1) Status (conectividad + UISP)
    print("1) /status")
    r = requests.post(
        f"{API_BASE}/status",
        json={"ip_list": ["45.172.141.122", "45.172.141.35"]},
    )
    pretty(r)

    # 2) Topología troncal
    print("2) /trunk")
    r = requests.post(
        f"{API_BASE}/trunk",
        json={"ip_list": ["45.172.141.122", "45.172.141.35"]},
    )
    pretty(r)

    # 3) Topología enriquecida
    print("3) /topology")
    r = requests.post(
        f"{API_BASE}/topology",
        json={"ip_list": ["45.172.141.122", "45.172.141.35"]},
    )
    pretty(r)

    # 4) (Opcional) Test capacidad: aquí deberías tener ya lista una lista de clientes
    clients = ["172.24.76.21", "172.24.51.101"]  # ajusta según tu CSV
    print("4) /run")
    r = requests.post(
        f"{API_BASE}/run",
        json={
            "router_ips": ["45.172.141.122", "45.172.141.35"],
            "client_ips": clients,
        },
    )
    pretty(r)


if __name__ == "__main__":
    print("Esperando a que arranque el servidor en http://localhost:8000 …")
    time.sleep(2)
    main()

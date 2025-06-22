import pandas as pd

from app.services.client_service import associate_clients_to_devices

# Simulamos dispositivos UISP
DEVICES = [
    {
        "ipAddress": "192.168.1.10",
        "identification": {
            "id": 1,
            "hostname": "dev1",
            "mac": "AA:BB:CC:DD:EE:FF",
            "name": "Cliente1",
        },
    },
    {
        "ipAddress": "192.168.1.20",
        "identification": {
            "id": 2,
            "hostname": "dev2",
            "mac": "11:22:33:44:55:66",
            "name": "ClienteDos",
        },
    },
    {
        "ipAddress": "10.0.0.5",
        "identification": {
            "id": 3,
            "hostname": "dev3",
            "mac": "77:88:99:AA:BB:CC",
            "name": "Otro",
        },
    },
]


def make_df(rows):
    return pd.DataFrame(rows)


def test_ip_exact_match():
    df = make_df([{"nombre": "X", "ip": "192.168.1.10", "mac": "", "plan": ""}])
    out = associate_clients_to_devices(df, DEVICES)
    assert out[0]["matched"]
    assert out[0]["método"] == "ip_exact"
    assert out[0]["dispositivo_id"] == 1


def test_mac_exact_match():
    df = make_df([{"nombre": "Y", "ip": "", "mac": "11:22:33:44:55:66", "plan": ""}])
    out = associate_clients_to_devices(df, DEVICES)
    assert out[0]["matched"]
    assert out[0]["método"] == "mac_exact"
    assert out[0]["dispositivo_id"] == 2


def test_name_exact_match():
    df = make_df([{"nombre": "Cliente1", "ip": "", "mac": "", "plan": ""}])
    out = associate_clients_to_devices(df, DEVICES)
    assert out[0]["matched"]
    assert out[0]["método"] == "name_exact"
    assert out[0]["uisp_name"] == "Cliente1"


def test_subnet_24_match():
    df = make_df([{"nombre": "Z", "ip": "192.168.1.99", "mac": "", "plan": ""}])
    out = associate_clients_to_devices(df, DEVICES)
    assert out[0]["matched"]
    assert out[0]["método"] == "subnet_24"
    # 192.168.1.99 comparte /24 con 192.168.1.10


def test_name_fuzzy_match():
    df = make_df([{"nombre": "clientedos", "ip": "", "mac": "", "plan": ""}])
    out = associate_clients_to_devices(df, DEVICES, fuzzy_threshold=0.7)
    assert out[0]["matched"]
    assert out[0]["método"] == "name_fuzzy"
    assert out[0]["similarity"] >= 0.8

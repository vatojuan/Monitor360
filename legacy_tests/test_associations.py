#!/usr/bin/env python3
# File: test_associations.py

import pandas as pd

from app.services.associate_clients import associate_clients_to_devices
from app.services.uisp_service import get_uisp_devices
from app.utils.clientes_loader import load_clients_csv


def main():
    # 1. Cargar clientes
    clientes_df = load_clients_csv()  # por defecto lee "Lista de Usuarios.csv"

    # 2. Obtener dispositivos desde UISP
    devices = get_uisp_devices()

    # 3. Asociar clientes con dispositivos
    asociaciones = associate_clients_to_devices(clientes_df, devices)

    # 4. Mostrar resultados por consola
    print(f"\n🔗 Asociaciones encontradas: {len(asociaciones)}\n")
    for a in asociaciones:
        print(f"✔️ Cliente {a['nombre']} ({a['ip']}) → {a['hostname']} [{a['mac']}]")

    # 5. Guardar en CSV
    if asociaciones:
        df_out = pd.DataFrame(asociaciones)
        df_out.to_csv("asociaciones.csv", index=False, encoding="utf-8")
        print("\n📁 Archivo asociaciones.csv guardado correctamente.")
    else:
        print("\n⚠️ No se encontraron asociaciones.")


if __name__ == "__main__":
    main()

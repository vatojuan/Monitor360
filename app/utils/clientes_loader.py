# File: app/utils/clientes_loader.py

import pandas as pd


def load_clients_csv(file_path: str = "Lista de Usuarios.csv") -> pd.DataFrame:
    """
    Carga y normaliza el CSV exportado desde MikroWisp.
    """
    df = pd.read_csv(file_path)
    df.columns = (
        df.columns.str.lower().str.strip()
    )  # Asegura nombres de columnas consistentes
    return df

#!/usr/bin/env python3
# File: test_credentials.py

import logging
import os
import sys

import requests
from dotenv import load_dotenv

# Importar tus módulos internos
from app.supabase_client import supabase
from app.utils.mikrotik_connect import try_mikrotik_passwords

# Cargar .env
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("test_credentials")


def test_mikrotik():
    host = os.getenv("MIKROTIK_HOST")
    user = os.getenv("MIKROTIK_USER", "admin")
    passwords = os.getenv("MIKROTIK_PASSWORDS", "").split(",")
    port = int(os.getenv("MIKROTIK_PORT", "8728"))

    logger.info("🔑 Probando MikroTik credentials...")
    ok = False
    for pwd in passwords:
        pwd = pwd.strip()
        if not pwd:
            continue
        logger.info(f"  🔍 Probar contraseña «{pwd}»")
        api = try_mikrotik_passwords(host, user, [pwd], port)
        if api:
            logger.info("  ✅ Conexión exitosa a MikroTik")
            ok = True
            break
        else:
            logger.info(f"  ❌ Falló contraseña «{pwd}»")
    if not ok:
        logger.error("  🚨 Todas las contraseñas fallaron.")
    return ok


def test_uisp():
    logger.info("🌐 Probando API UISP...")
    token = os.getenv("UISP_TOKEN") or os.getenv("UISP_LEGACY_TOKEN")
    base_url = os.getenv("UISP_URL")
    if not base_url or not token:
        logger.error("  ⚠️ Debes definir UISP_URL y UISP_TOKEN en el .env")
        return False

    url = f"{base_url}/nms/api/v2.1/devices"
    headers = {"X-Auth-Token": token}
    logger.info(f"  → GET {url}")
    logger.info(f"  → HEADERS: {headers}")
    resp = requests.get(url, headers=headers, timeout=10, verify=False)
    logger.info(f"  ← Status: {resp.status_code} {resp.reason}")
    logger.info(f"  ← Response body (truncado a 500 chars):\n{resp.text[:500]}")

    try:
        resp.raise_for_status()
        devices = resp.json()
        if isinstance(devices, list):
            logger.info(f"  ✅ UISP respondió con {len(devices)} dispositivos")
        else:
            logger.info(
                "  ⚠️ UISP respondió correctamente, pero el formato no es una lista."
            )
        return True
    except requests.HTTPError as e:
        logger.error(f"  🚨 HTTPError: {e}")
        return False
    except ValueError as e:
        logger.error(f"  🚨 No se pudo parsear JSON: {e}")
        return False


def test_supabase():
    logger.info("🐘 Probando Supabase...")
    try:
        resp = supabase.table("alarmas").select("*").limit(1).execute()
        if hasattr(resp, "data"):
            if resp.data:
                logger.info("  ✅ Supabase respondió correctamente con datos.")
            else:
                logger.warning(
                    "  ⚠️ Supabase respondió pero la tabla 'alarmas' está vacía."
                )
            return True
        else:
            logger.error("  🚨 Respuesta inesperada de Supabase.")
            return False
    except Exception as e:
        logger.error(f"  🚨 Supabase error: {e}")
        return False


def test_telegram():
    logger.info("📨 Telegram getMe test...")
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("  🚨 TELEGRAM_BOT_TOKEN no definido")
        return False
    url = f"https://api.telegram.org/bot{token}/getMe"
    logger.info(f"  → GET {url}")
    try:
        r = requests.get(url, timeout=5)
        j = r.json()
        logger.info(f"  ← Status: {r.status_code}, Response: {j}")
        if r.status_code == 200 and j.get("ok"):
            logger.info(f"  ✅ Telegram conectado como @{j['result']['username']}")
            return True
        else:
            logger.error(f"  🚨 Telegram error: {j}")
            return False
    except Exception as e:
        logger.error(f"  🚨 Telegram excepción: {e}")
        return False


if __name__ == "__main__":
    all_ok = True
    all_ok &= test_mikrotik()
    all_ok &= test_uisp()
    all_ok &= test_supabase()
    all_ok &= test_telegram()
    sys.exit(0 if all_ok else 1)

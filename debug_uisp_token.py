import os

import requests
import urllib3
from dotenv import load_dotenv

# Evitar warnings de SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

url = os.getenv("UISP_URL", "").rstrip("/") + "/nms/api/v2.1/devices"
token = os.getenv("UISP_LEGACY_TOKEN")
headers = {"X-Auth-Token": token}

print("🌐 TEST MANUAL API UISP")
print(f"→ URL: {url}")
print(f"→ TOKEN: {token}")
print(f"→ HEADERS: {headers}")

try:
    r = requests.get(url, headers=headers, timeout=10, verify=False)
    print(f"← STATUS: {r.status_code}")
    print(f"← RESPONSE:\n{r.text[:500]}")
except Exception as e:
    print(f"❌ EXCEPCIÓN: {e}")

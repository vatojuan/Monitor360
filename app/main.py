#!/usr/bin/env python3
"""
Punto de entrada FastAPI para Monitor360.

- Expone rutas de monitoreo, alarmas y topología.
- Habilita CORS para permitir el consumo desde el frontend (Next.js).
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.alarms import router as alarms_router

# Routers ─────────────────────────────────────────────────────────────
from app.routers.monitoring import router as monitoring_router
from app.routers.topologia import router as topologia_router

# ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Monitor360",
    description="Sistema profesional de monitoreo de red para ISPs",
    version="1.0.0",
)

# CORS (ajusta allow_origins si quieres restringir a tu dominio)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ej. ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health-check simple ─────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root() -> dict[str, str]:
    return {"status": "Sistema de monitoreo activo"}


# Enrutado de la API ──────────────────────────────────────────────────
app.include_router(monitoring_router, prefix="/api/monitoring", tags=["Monitoreo"])
app.include_router(alarms_router, prefix="/api/alarms", tags=["Alarmas"])
app.include_router(topologia_router, prefix="/api", tags=["Topología"])

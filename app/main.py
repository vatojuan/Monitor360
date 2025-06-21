# File: app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import status
from app.routers.alarms import router as alarms_router

# Importa aquí los routers con rutas absolutas
from app.routers.monitoring import router as monitoring_router
from app.routers.topologia import router as topologia_router  # <-- NUEVO

app = FastAPI(
    title="Monitor360",
    description="Sistema profesional de monitoreo de red para ISPs",
    version="1.0.0",
)

# CORS para permitir conexión desde el frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # o especificar orígenes como ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Ruta base
@app.get("/")
def root():
    return {"status": "Sistema de monitoreo activo"}


# Rutas
app.include_router(monitoring_router, prefix="/api/monitoring", tags=["Monitoreo"])
app.include_router(alarms_router, prefix="/api/alarms", tags=["Alarmas"])
app.include_router(topologia_router, prefix="/api", tags=["Topología"])  # <-- NUEVO
app.include_router(status.router)

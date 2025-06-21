import os

from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/api/status", tags=["Status"])


@router.get("/", summary="Health Check")
async def health_check():
    return JSONResponse(
        content={"status": "ok", "version": os.getenv("MONITOR360_VERSION", "0.1.0")}
    )

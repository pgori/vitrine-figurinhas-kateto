from fastapi import FastAPI

from app.routers.health import router as health_router

app = FastAPI(
    title="Vitrine de Figurinhas Kateto API",
    version="0.1.0",
)

app.include_router(health_router)


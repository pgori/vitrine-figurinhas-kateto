from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers.auth import router as auth_router
from app.routers.health import router as health_router
from app.routers.leads import router as leads_router

app = FastAPI(
    title="Vitrine de Figurinhas Kateto API",
    version="0.1.0",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"detail": jsonable_encoder(exc.errors())},
    )


app.include_router(auth_router)
app.include_router(health_router)
app.include_router(leads_router)

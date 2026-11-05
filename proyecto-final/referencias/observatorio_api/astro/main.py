"""Composition root: configuración, ciclo de vida, middleware y routers."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .config import Settings
from .database import crear_engine
from .middleware import trazabilidad
from .routers import auth, observaciones


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()
    engine = crear_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # ¿create_all modifica tablas existentes? No: para eso se usan migraciones.
        SQLModel.metadata.create_all(engine)
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(title="Bitácora del observatorio", version="1.0.0", lifespan=lifespan)
    app.state.settings = settings
    app.state.engine = engine
    app.middleware("http")(trazabilidad)
    app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins,
                       allow_methods=["GET", "POST", "PATCH", "DELETE"],
                       allow_headers=["Authorization", "Content-Type"],
                       expose_headers=["X-Request-ID", "X-Process-Time"])
    app.include_router(auth.router)
    app.include_router(observaciones.router)

    @app.get("/salud", tags=["Sistema"])
    def salud():
        """Liveness: el proceso responde; no verifica disponibilidad de la BD."""
        return {"estado": "ok"}

    return app

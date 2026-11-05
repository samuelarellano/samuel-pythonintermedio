"""Composition Root de La Estrellita: configuración, ciclo de vida, middleware y routers."""
from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .api.routers import auth, productos, proveedores
from .infrastructure.config import Settings
from .infrastructure.database import crear_engine
from .infrastructure.middleware import trazabilidad_middleware


def create_app(settings: Settings | None = None) -> FastAPI:
    """Fábrica de aplicación con ciclo de vida asíncrono y configuración tipada."""
    settings = settings or Settings()
    engine = crear_engine(settings.database_url)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Advertencia académica: create_all crea tablas ausentes, no migra existentes.
        SQLModel.metadata.create_all(engine)
        try:
            yield
        finally:
            engine.dispose()

    app = FastAPI(
        title="La Estrellita - Catálogo de Proveedores y Productos",
        version="1.0.0",
        description="API REST modular para gestión de catálogos comerciales con FastAPI y SQLModel.",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.engine = engine

    # Middleware transversal
    app.middleware("http")(trazabilidad_middleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type"],
        expose_headers=["X-Request-ID", "X-Process-Time"],
    )

    # Endpoint público de liveness
    @app.get("/salud", tags=["Sistema"])
    def salud():
        """Comprueba que el proceso responde (liveness); no expone estado de base de datos."""
        return {"estado": "ok"}

    # Router base bajo /api/v1
    api_v1 = APIRouter(prefix="/api/v1")
    api_v1.include_router(auth.router)
    api_v1.include_router(proveedores.router)
    api_v1.include_router(productos.router)
    app.include_router(api_v1)

    return app

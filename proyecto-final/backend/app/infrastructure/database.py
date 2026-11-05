"""Gestión del motor de base de datos SQLite y sesiones por petición."""
from collections.abc import Generator
from fastapi import Request
from sqlalchemy import event
from sqlmodel import Session, create_engine


def crear_engine(url: str):
    """Crea el engine de SQLModel/SQLAlchemy con claves foráneas activas en SQLite."""
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=args)

    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def activar_foreign_keys(dbapi_connection, _):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def get_session(request: Request) -> Generator[Session, None, None]:
    """Generador de sesión por petición.

    La sesión se cierra de manera determinista al terminar el ciclo de vida del request.
    Las mutaciones deben realizar commit explícito.
    """
    with Session(request.app.state.engine) as session:
        yield session

"""Un engine compartido; una Session distinta por petición."""
from fastapi import Request
from sqlalchemy import event
from sqlmodel import Session, create_engine


def crear_engine(url: str):
    args = {"check_same_thread": False} if url.startswith("sqlite") else {}
    engine = create_engine(url, connect_args=args)
    if url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def activar_foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
    return engine


def get_session(request: Request):
    # ¿yield hace commit? No. Las escrituras confirman explícitamente.
    with Session(request.app.state.engine) as session:
        yield session

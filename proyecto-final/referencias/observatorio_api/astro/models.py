"""Tablas persistentes. Los contratos HTTP viven aparte, en schemas.py."""
from sqlmodel import Field, SQLModel


class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    password_hash: str


class Observacion(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    objeto: str = Field(index=True)
    notas: str
    propietario_id: int = Field(foreign_key="usuario.id", index=True)
    # ¿Por qué no recibir propietario_id del cliente? La identidad viene del token.

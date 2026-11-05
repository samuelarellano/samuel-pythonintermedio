"""Tablas de base de datos persistentes con SQLModel."""
from sqlmodel import Field, SQLModel, UniqueConstraint


class UsuarioTable(SQLModel, table=True):
    """Tabla persistente de usuarios."""
    __tablename__ = "usuarios"

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=40)
    password_hash: str = Field(max_length=255)


class ProveedorTable(SQLModel, table=True):
    """Tabla persistente de proveedores vinculados a un usuario propietario."""
    __tablename__ = "proveedores"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=120)
    contacto: str = Field(max_length=120)
    telefono: str = Field(max_length=20)
    propietario_id: int = Field(foreign_key="usuarios.id", index=True)


class ProductoTable(SQLModel, table=True):
    """Tabla persistente de productos con unicidad de código por usuario propietario."""
    __tablename__ = "productos"
    __table_args__ = (
        UniqueConstraint("propietario_id", "codigo", name="uq_producto_propietario_codigo"),
    )

    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, max_length=40)
    nombre: str = Field(index=True, max_length=120)
    categoria: str = Field(index=True, max_length=60)
    precio_centavos: int = Field(gt=0)
    proveedor_id: int = Field(foreign_key="proveedores.id", index=True)
    propietario_id: int = Field(foreign_key="usuarios.id", index=True)

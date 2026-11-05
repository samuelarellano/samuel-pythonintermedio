"""Contratos HTTP para el catálogo de Productos con Pydantic v2."""
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProductoCrear(BaseModel):
    """Contrato de entrada para crear un producto asociado a un proveedor."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    codigo: str = Field(
        min_length=1,
        max_length=40,
        pattern=r"^[A-Za-z0-9_-]+$",
        description="Código único dentro del catálogo del usuario",
    )
    nombre: str = Field(min_length=1, max_length=120, description="Nombre descriptivo del producto")
    categoria: str = Field(min_length=1, max_length=60, description="Categoría o rubro")
    precio_centavos: int = Field(gt=0, description="Precio entero en centavos mayor que cero")
    proveedor_id: int = Field(gt=0, description="Identificador del proveedor asociado")


class ProductoActualizar(BaseModel):
    """Contrato de entrada para actualización parcial (PATCH).

    Si un campo se omite, se conserva su valor actual.
    Si se envía null explícito, se rechaza con 422.
    """
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    codigo: str | None = Field(default=None, min_length=1, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    categoria: str | None = Field(default=None, min_length=1, max_length=60)
    precio_centavos: int | None = Field(default=None, gt=0)
    proveedor_id: int | None = Field(default=None, gt=0)

    @field_validator("codigo", "nombre", "categoria", "precio_centavos", "proveedor_id")
    @classmethod
    def no_null(cls, value):
        if value is None:
            raise ValueError("Omite el campo si no quieres modificarlo")
        return value


class ProductoResponse(BaseModel):
    """Contrato de salida para producto; nunca expone propietario_id."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nombre: str
    categoria: str
    precio_centavos: int
    proveedor_id: int

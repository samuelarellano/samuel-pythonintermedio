"""Contratos HTTP para el catálogo de Proveedores con Pydantic v2."""
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProveedorCrear(BaseModel):
    """Contrato de entrada para crear un proveedor."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nombre: str = Field(min_length=1, max_length=120, description="Razón social o nombre comercial")
    contacto: str = Field(min_length=1, max_length=120, description="Nombre de la persona de contacto")
    telefono: str = Field(min_length=7, max_length=20, description="Teléfono de contacto")


class ProveedorActualizar(BaseModel):
    """Contrato de entrada para actualización parcial (PATCH).

    Si un campo se omite, se conserva su valor actual.
    Si se envía null explícito, se rechaza con 422.
    """
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    nombre: str | None = Field(default=None, min_length=1, max_length=120)
    contacto: str | None = Field(default=None, min_length=1, max_length=120)
    telefono: str | None = Field(default=None, min_length=7, max_length=20)

    @field_validator("nombre", "contacto", "telefono")
    @classmethod
    def no_null(cls, value):
        if value is None:
            raise ValueError("Omite el campo si no quieres modificarlo")
        return value


class ProveedorResponse(BaseModel):
    """Contrato de salida para proveedor público; nunca expone propietario_id."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    contacto: str
    telefono: str

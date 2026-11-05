"""Contratos de entrada/salida; un hash jamás forma parte de UsuarioPublico."""
from pydantic import BaseModel, ConfigDict, Field, field_validator


class Registro(BaseModel):
    model_config = ConfigDict(extra="forbid")
    username: str = Field(min_length=3, max_length=40, pattern=r"^[a-z0-9_]+$")
    # No se recortan espacios de la contraseña: también pueden ser significativos.
    password: str = Field(min_length=12, max_length=128)

class UsuarioPublico(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ObservacionCrear(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    objeto: str = Field(min_length=1, max_length=100)
    notas: str = Field(min_length=1, max_length=2000)


class ObservacionPublica(ObservacionCrear):
    model_config = ConfigDict(from_attributes=True)
    id: int
    propietario_id: int


class ObservacionActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    objeto: str | None = Field(default=None, min_length=1, max_length=100)
    notas: str | None = Field(default=None, min_length=1, max_length=2000)

    @field_validator("objeto", "notas")
    @classmethod
    def no_null(cls, value):
        # ¿Omitir y enviar null significan lo mismo? No; null se rechaza.
        if value is None:
            raise ValueError("Omite el campo si no quieres modificarlo")
        return value

"""Esquemas HTTP para autenticación y usuarios con Pydantic v2."""
from pydantic import BaseModel, ConfigDict, Field


class RegistroRequest(BaseModel):
    """Contrato de entrada para registro de nuevo usuario."""
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    username: str = Field(
        min_length=3,
        max_length=40,
        pattern=r"^[a-z0-9_]+$",
        description="Nombre de usuario: minúsculas, números y guion bajo",
    )
    # No se recortan espacios en blanco en la contraseña: pueden ser intencionales
    password: str = Field(
        min_length=12,
        max_length=128,
        description="Contraseña: mínimo 12 caracteres",
    )


class TokenResponse(BaseModel):
    """Contrato de salida para token Bearer."""
    access_token: str
    token_type: str = "bearer"


class UsuarioResponse(BaseModel):
    """Contrato de salida de perfil público; nunca expone password_hash ni secretos."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str

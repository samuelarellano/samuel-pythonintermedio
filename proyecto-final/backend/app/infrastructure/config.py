"""Configuración tipada mediante pydantic-settings.

Valida variables de entorno y rechaza secretos inseguros o marcadores de ejemplo.
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
    database_url: str = "sqlite:///./la_estrellita.db"
    jwt_secret: str = Field(
        default="cambiar_este_secreto_por_un_token_hex_seguro_de_32_bytes_minimo",
        min_length=32,
    )
    token_minutes: int = Field(default=30, ge=1, le=120)
    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("jwt_secret")
    @classmethod
    def validar_secreto(cls, value: str) -> str:
        if value.startswith("REEMPLAZAR"):
            raise ValueError("Genera un JWT_SECRET real antes de arrancar")
        return value

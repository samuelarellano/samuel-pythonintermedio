"""Configuración externa: nunca guardar secretos reales en Git."""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    database_url: str = "sqlite:///./observatorio.db"
    jwt_secret: str = Field(min_length=32)
    token_minutes: int = Field(default=30, ge=1, le=120)
    cors_origins: list[str] = ["http://localhost:5173"]

    @field_validator("jwt_secret")
    @classmethod
    def secret_real(cls, value: str) -> str:
        # ¿Basta la longitud? No: rechazamos también el marcador del ejemplo.
        if value.startswith("REEMPLAZAR"):
            raise ValueError("Genera JWT_SECRET siguiendo el README")
        return value

"""Entidad pura de dominio Usuario y sus invariantes."""
from dataclasses import dataclass
import re

USERNAME_REGEX = re.compile(r"^[a-z0-9_]+$")


@dataclass(frozen=True)
class Usuario:
    """Entidad de dominio Usuario."""
    id: int | None
    username: str

    def __post_init__(self):
        if not (3 <= len(self.username) <= 40):
            raise ValueError("El nombre de usuario debe tener entre 3 y 40 caracteres")
        if not USERNAME_REGEX.match(self.username):
            raise ValueError("El nombre de usuario solo admite letras minúsculas, números y guion bajo")

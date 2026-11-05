"""Entidad pura de dominio Proveedor."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Proveedor:
    """Entidad de dominio Proveedor con validación de invariantes."""
    id: int | None
    nombre: str
    contacto: str
    telefono: str
    propietario_id: int

    def __post_init__(self):
        nombre_limpio = self.nombre.strip() if self.nombre else ""
        if not (1 <= len(nombre_limpio) <= 120):
            raise ValueError("El nombre del proveedor no puede estar vacío y debe tener máximo 120 caracteres")

        contacto_limpio = self.contacto.strip() if self.contacto else ""
        if not (1 <= len(contacto_limpio) <= 120):
            raise ValueError("El contacto del proveedor no puede estar vacío y debe tener máximo 120 caracteres")

        telefono_limpio = self.telefono.strip() if self.telefono else ""
        if not (7 <= len(telefono_limpio) <= 20):
            raise ValueError("El teléfono del proveedor debe tener entre 7 y 20 caracteres")

        if self.propietario_id <= 0:
            raise ValueError("El propietario_id debe ser un entero positivo")

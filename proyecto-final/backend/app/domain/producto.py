"""Entidad pura de dominio Producto y sus invariantes."""
from dataclasses import dataclass
import re

CODIGO_REGEX = re.compile(r"^[A-Za-z0-9_-]+$")


@dataclass(frozen=True)
class Producto:
    """Entidad de dominio Producto."""
    id: int | None
    codigo: str
    nombre: str
    categoria: str
    precio_centavos: int
    proveedor_id: int
    propietario_id: int

    def __post_init__(self):
        codigo_limpio = self.codigo.strip() if self.codigo else ""
        if not (1 <= len(codigo_limpio) <= 40):
            raise ValueError("El código del producto debe tener entre 1 y 40 caracteres")
        if not CODIGO_REGEX.match(codigo_limpio):
            raise ValueError("El código de producto solo admite caracteres alfanuméricos, guiones y guiones bajos")

        nombre_limpio = self.nombre.strip() if self.nombre else ""
        if not (1 <= len(nombre_limpio) <= 120):
            raise ValueError("El nombre del producto no puede estar vacío y debe tener máximo 120 caracteres")

        categoria_limpia = self.categoria.strip() if self.categoria else ""
        if not (1 <= len(categoria_limpia) <= 60):
            raise ValueError("La categoría del producto no puede estar vacía y debe tener máximo 60 caracteres")

        if not isinstance(self.precio_centavos, int) or isinstance(self.precio_centavos, bool):
            raise ValueError("El precio en centavos debe ser un número entero (prohibido float)")

        if self.precio_centavos <= 0:
            raise ValueError("El precio en centavos debe ser estrictamente mayor que cero")

        if self.proveedor_id <= 0:
            raise ValueError("El proveedor_id debe ser un entero positivo")

        if self.propietario_id <= 0:
            raise ValueError("El propietario_id debe ser un entero positivo")

"""Casos de uso del catálogo de Proveedores.

Independientes de frameworks web (FastAPI) y de ORM (SQLModel).
"""
from ...domain.exceptions import ProveedorConProductosError, ProveedorNoEncontrado
from ...domain.proveedor import Proveedor
from ..interfaces.producto_repo import IProductoRepository
from ..interfaces.proveedor_repo import IProveedorRepository


class ProveedorUseCases:
    """Orquestador de casos de uso para proveedores."""

    def __init__(
        self,
        repo: IProveedorRepository,
        producto_repo: IProductoRepository | None = None,
    ):
        self.repo = repo
        self.producto_repo = producto_repo

    def crear(self, nombre: str, contacto: str, telefono: str, propietario_id: int) -> Proveedor:
        proveedor = Proveedor(
            id=None,
            nombre=nombre,
            contacto=contacto,
            telefono=telefono,
            propietario_id=propietario_id,
        )
        return self.repo.crear(proveedor)

    def listar(self, propietario_id: int, q: str | None = None, offset: int = 0, limite: int = 20) -> list[Proveedor]:
        return self.repo.listar(propietario_id=propietario_id, q=q, offset=offset, limite=limite)

    def obtener_por_id(self, proveedor_id: int, propietario_id: int) -> Proveedor:
        proveedor = self.repo.obtener_por_id(proveedor_id, propietario_id)
        if proveedor is None:
            raise ProveedorNoEncontrado("Proveedor no encontrado")
        return proveedor

    def actualizar(
        self,
        proveedor_id: int,
        propietario_id: int,
        nombre: str | None = None,
        contacto: str | None = None,
        telefono: str | None = None,
    ) -> Proveedor:
        actual = self.obtener_por_id(proveedor_id, propietario_id)

        nuevo_nombre = nombre if nombre is not None else actual.nombre
        nuevo_contacto = contacto if contacto is not None else actual.contacto
        nuevo_telefono = telefono if telefono is not None else actual.telefono

        actualizado = Proveedor(
            id=actual.id,
            nombre=nuevo_nombre,
            contacto=nuevo_contacto,
            telefono=nuevo_telefono,
            propietario_id=actual.propietario_id,
        )
        return self.repo.actualizar(actualizado)

    def eliminar(self, proveedor_id: int, propietario_id: int) -> None:
        self.obtener_por_id(proveedor_id, propietario_id)

        if self.producto_repo and self.producto_repo.contar_por_proveedor(proveedor_id, propietario_id) > 0:
            raise ProveedorConProductosError("No se puede eliminar el proveedor porque tiene productos asociados")

        eliminado = self.repo.eliminar(proveedor_id, propietario_id)
        if not eliminado:
            raise ProveedorNoEncontrado("Proveedor no encontrado")

"""Casos de uso del catálogo de Productos.

Independientes de frameworks web y de ORM.
"""
from ...domain.exceptions import ProductoNoEncontrado, ProveedorNoEncontrado
from ...domain.producto import Producto
from ..interfaces.producto_repo import IProductoRepository
from ..interfaces.proveedor_repo import IProveedorRepository


class ProductoUseCases:
    """Orquestador de lógica de negocio para productos."""

    def __init__(self, producto_repo: IProductoRepository, proveedor_repo: IProveedorRepository):
        self.producto_repo = producto_repo
        self.proveedor_repo = proveedor_repo

    def crear(
        self,
        codigo: str,
        nombre: str,
        categoria: str,
        precio_centavos: int,
        proveedor_id: int,
        propietario_id: int,
    ) -> Producto:
        # Validación de relación cruzada: el proveedor debe existir y pertenecer al mismo usuario
        proveedor = self.proveedor_repo.obtener_por_id(proveedor_id, propietario_id)
        if proveedor is None:
            raise ProveedorNoEncontrado("Proveedor no encontrado en tu catálogo")

        producto = Producto(
            id=None,
            codigo=codigo,
            nombre=nombre,
            categoria=categoria,
            precio_centavos=precio_centavos,
            proveedor_id=proveedor_id,
            propietario_id=propietario_id,
        )
        return self.producto_repo.crear(producto)

    def listar(
        self,
        propietario_id: int,
        q: str | None = None,
        categoria: str | None = None,
        proveedor_id: int | None = None,
        offset: int = 0,
        limite: int = 20,
    ) -> list[Producto]:
        return self.producto_repo.listar(
            propietario_id=propietario_id,
            q=q,
            categoria=categoria,
            proveedor_id=proveedor_id,
            offset=offset,
            limite=limite,
        )

    def obtener_por_id(self, producto_id: int, propietario_id: int) -> Producto:
        producto = self.producto_repo.obtener_por_id(producto_id, propietario_id)
        if producto is None:
            raise ProductoNoEncontrado("Producto no encontrado")
        return producto

    def actualizar(
        self,
        producto_id: int,
        propietario_id: int,
        codigo: str | None = None,
        nombre: str | None = None,
        categoria: str | None = None,
        precio_centavos: int | None = None,
        proveedor_id: int | None = None,
    ) -> Producto:
        actual = self.obtener_por_id(producto_id, propietario_id)

        # Si se actualiza el proveedor, verificar que el nuevo proveedor pertenezca al usuario
        nuevo_proveedor_id = actual.proveedor_id
        if proveedor_id is not None and proveedor_id != actual.proveedor_id:
            proveedor = self.proveedor_repo.obtener_por_id(proveedor_id, propietario_id)
            if proveedor is None:
                raise ProveedorNoEncontrado("El nuevo proveedor no existe en tu catálogo")
            nuevo_proveedor_id = proveedor_id

        actualizado = Producto(
            id=actual.id,
            codigo=codigo if codigo is not None else actual.codigo,
            nombre=nombre if nombre is not None else actual.nombre,
            categoria=categoria if categoria is not None else actual.categoria,
            precio_centavos=precio_centavos if precio_centavos is not None else actual.precio_centavos,
            proveedor_id=nuevo_proveedor_id,
            propietario_id=actual.propietario_id,
        )
        return self.producto_repo.actualizar(actualizado)

    def eliminar(self, producto_id: int, propietario_id: int) -> None:
        self.obtener_por_id(producto_id, propietario_id)
        eliminado = self.producto_repo.eliminar(producto_id, propietario_id)
        if not eliminado:
            raise ProductoNoEncontrado("Producto no encontrado")

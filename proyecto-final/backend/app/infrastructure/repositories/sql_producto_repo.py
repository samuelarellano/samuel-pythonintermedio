"""Implementación del repositorio de productos con SQLModel y SQLite."""
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from ...domain.exceptions import CodigoProductoDuplicado
from ...domain.producto import Producto
from ..models import ProductoTable


class SqlProductoRepository:
    """Adaptador de persistencia para productos."""

    def __init__(self, session: Session):
        self.session = session

    def _a_dominio(self, record: ProductoTable) -> Producto:
        return Producto(
            id=record.id,
            codigo=record.codigo,
            nombre=record.nombre,
            categoria=record.categoria,
            precio_centavos=record.precio_centavos,
            proveedor_id=record.proveedor_id,
            propietario_id=record.propietario_id,
        )

    def crear(self, producto: Producto) -> Producto:
        record = ProductoTable(
            codigo=producto.codigo,
            nombre=producto.nombre,
            categoria=producto.categoria,
            precio_centavos=producto.precio_centavos,
            proveedor_id=producto.proveedor_id,
            propietario_id=producto.propietario_id,
        )
        self.session.add(record)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise CodigoProductoDuplicado("Código de producto ya registrado en tu catálogo") from None

        self.session.refresh(record)
        return self._a_dominio(record)

    def obtener_por_id(self, producto_id: int, propietario_id: int) -> Producto | None:
        query = select(ProductoTable).where(
            ProductoTable.id == producto_id,
            ProductoTable.propietario_id == propietario_id,
        )
        record = self.session.exec(query).first()
        return self._a_dominio(record) if record else None

    def obtener_por_codigo(self, codigo: str, propietario_id: int) -> Producto | None:
        query = select(ProductoTable).where(
            ProductoTable.codigo == codigo,
            ProductoTable.propietario_id == propietario_id,
        )
        record = self.session.exec(query).first()
        return self._a_dominio(record) if record else None

    def listar(
        self,
        propietario_id: int,
        q: str | None = None,
        categoria: str | None = None,
        proveedor_id: int | None = None,
        offset: int = 0,
        limite: int = 20,
    ) -> list[Producto]:
        query = select(ProductoTable).where(ProductoTable.propietario_id == propietario_id)
        if q:
            filtro_texto = or_(
                ProductoTable.nombre.contains(q, autoescape=True),
                ProductoTable.codigo.contains(q, autoescape=True),
            )
            query = query.where(filtro_texto)
        if categoria:
            query = query.where(ProductoTable.categoria == categoria)
        if proveedor_id:
            query = query.where(ProductoTable.proveedor_id == proveedor_id)

        query = query.order_by(ProductoTable.id).offset(offset).limit(limite)
        records = self.session.exec(query).all()
        return [self._a_dominio(r) for r in records]

    def actualizar(self, producto: Producto) -> Producto:
        query = select(ProductoTable).where(
            ProductoTable.id == producto.id,
            ProductoTable.propietario_id == producto.propietario_id,
        )
        record = self.session.exec(query).first()
        if not record:
            raise ValueError("Registro de producto no encontrado para actualizar")

        record.codigo = producto.codigo
        record.nombre = producto.nombre
        record.categoria = producto.categoria
        record.precio_centavos = producto.precio_centavos
        record.proveedor_id = producto.proveedor_id

        self.session.add(record)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise CodigoProductoDuplicado("Código de producto ya registrado en tu catálogo") from None

        self.session.refresh(record)
        return self._a_dominio(record)

    def eliminar(self, producto_id: int, propietario_id: int) -> bool:
        query = select(ProductoTable).where(
            ProductoTable.id == producto_id,
            ProductoTable.propietario_id == propietario_id,
        )
        record = self.session.exec(query).first()
        if not record:
            return False

        self.session.delete(record)
        self.session.commit()
        return True

    def contar_por_proveedor(self, proveedor_id: int, propietario_id: int) -> int:
        query = select(func.count(ProductoTable.id)).where(
            ProductoTable.proveedor_id == proveedor_id,
            ProductoTable.propietario_id == propietario_id,
        )
        resultado = self.session.exec(query).first()
        return resultado or 0

"""Implementación del repositorio de proveedores con SQLModel y SQLite."""
from sqlmodel import Session, select
from ...domain.proveedor import Proveedor
from ..models import ProveedorTable


class SqlProveedorRepository:
    """Adaptador de persistencia para proveedores usando Session de SQLModel."""

    def __init__(self, session: Session):
        self.session = session

    def _a_dominio(self, record: ProveedorTable) -> Proveedor:
        return Proveedor(
            id=record.id,
            nombre=record.nombre,
            contacto=record.contacto,
            telefono=record.telefono,
            propietario_id=record.propietario_id,
        )

    def crear(self, proveedor: Proveedor) -> Proveedor:
        record = ProveedorTable(
            nombre=proveedor.nombre,
            contacto=proveedor.contacto,
            telefono=proveedor.telefono,
            propietario_id=proveedor.propietario_id,
        )
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return self._a_dominio(record)

    def obtener_por_id(self, proveedor_id: int, propietario_id: int) -> Proveedor | None:
        query = select(ProveedorTable).where(
            ProveedorTable.id == proveedor_id,
            ProveedorTable.propietario_id == propietario_id,
        )
        record = self.session.exec(query).first()
        return self._a_dominio(record) if record else None

    def listar(
        self,
        propietario_id: int,
        q: str | None = None,
        offset: int = 0,
        limite: int = 20,
    ) -> list[Proveedor]:
        query = select(ProveedorTable).where(ProveedorTable.propietario_id == propietario_id)
        if q:
            query = query.where(ProveedorTable.nombre.contains(q, autoescape=True))
        query = query.order_by(ProveedorTable.id).offset(offset).limit(limite)
        records = self.session.exec(query).all()
        return [self._a_dominio(r) for r in records]

    def actualizar(self, proveedor: Proveedor) -> Proveedor:
        query = select(ProveedorTable).where(
            ProveedorTable.id == proveedor.id,
            ProveedorTable.propietario_id == proveedor.propietario_id,
        )
        record = self.session.exec(query).first()
        if not record:
            raise ValueError("Registro no encontrado para actualizar")

        record.nombre = proveedor.nombre
        record.contacto = proveedor.contacto
        record.telefono = proveedor.telefono

        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return self._a_dominio(record)

    def eliminar(self, proveedor_id: int, propietario_id: int) -> bool:
        query = select(ProveedorTable).where(
            ProveedorTable.id == proveedor_id,
            ProveedorTable.propietario_id == propietario_id,
        )
        record = self.session.exec(query).first()
        if not record:
            return False

        self.session.delete(record)
        self.session.commit()
        return True

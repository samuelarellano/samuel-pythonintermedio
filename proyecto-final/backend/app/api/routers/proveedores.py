"""Router de operaciones CRUD para el catálogo de Proveedores."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response

from ...application.use_cases.proveedor_use_cases import ProveedorUseCases
from ...domain.exceptions import ProveedorConProductosError, ProveedorNoEncontrado
from ...infrastructure.repositories.sql_producto_repo import SqlProductoRepository
from ...infrastructure.repositories.sql_proveedor_repo import SqlProveedorRepository
from ..dependencies import SessionDep, UsuarioDep
from ..schemas.proveedor_schemas import ProveedorActualizar, ProveedorCrear, ProveedorResponse

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])
IdPath = Annotated[int, Path(gt=0, description="Identificador entero del proveedor mayor que cero")]


def get_proveedor_use_cases(session: SessionDep) -> ProveedorUseCases:
    """Fábrica de caso de uso inyectando los repositorios concretos."""
    repo = SqlProveedorRepository(session)
    producto_repo = SqlProductoRepository(session)
    return ProveedorUseCases(repo=repo, producto_repo=producto_repo)


@router.post("", response_model=ProveedorResponse, status_code=201)
def crear(
    datos: ProveedorCrear,
    usuario: UsuarioDep,
    use_cases: Annotated[ProveedorUseCases, Depends(get_proveedor_use_cases)],
):
    """Crea un nuevo proveedor asignando la propiedad al usuario autenticado."""
    return use_cases.crear(
        nombre=datos.nombre,
        contacto=datos.contacto,
        telefono=datos.telefono,
        propietario_id=usuario.id,
    )


@router.get("", response_model=list[ProveedorResponse])
def listar(
    usuario: UsuarioDep,
    use_cases: Annotated[ProveedorUseCases, Depends(get_proveedor_use_cases)],
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Lista únicamente los proveedores pertenecientes al usuario autenticado."""
    return use_cases.listar(
        propietario_id=usuario.id,
        q=q,
        offset=offset,
        limite=limite,
    )


@router.get("/{proveedor_id}", response_model=ProveedorResponse)
def obtener(
    proveedor_id: IdPath,
    usuario: UsuarioDep,
    use_cases: Annotated[ProveedorUseCases, Depends(get_proveedor_use_cases)],
):
    """Consulta el detalle de un proveedor propio. Si no existe o es ajeno, responde 404."""
    try:
        return use_cases.obtener_por_id(proveedor_id=proveedor_id, propietario_id=usuario.id)
    except ProveedorNoEncontrado:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado") from None


@router.patch("/{proveedor_id}", response_model=ProveedorResponse)
def actualizar(
    proveedor_id: IdPath,
    datos: ProveedorActualizar,
    usuario: UsuarioDep,
    use_cases: Annotated[ProveedorUseCases, Depends(get_proveedor_use_cases)],
):
    """Actualiza parcialmente un proveedor propio. Rechaza null en campos declarados."""
    try:
        return use_cases.actualizar(
            proveedor_id=proveedor_id,
            propietario_id=usuario.id,
            nombre=datos.nombre,
            contacto=datos.contacto,
            telefono=datos.telefono,
        )
    except ProveedorNoEncontrado:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado") from None


@router.delete("/{proveedor_id}", status_code=204)
def eliminar(
    proveedor_id: IdPath,
    usuario: UsuarioDep,
    use_cases: Annotated[ProveedorUseCases, Depends(get_proveedor_use_cases)],
):
    """Elimina un proveedor propio. Si tiene productos asociados, responde 409 Conflict."""
    try:
        use_cases.eliminar(proveedor_id=proveedor_id, propietario_id=usuario.id)
        return Response(status_code=204)
    except ProveedorNoEncontrado:
        raise HTTPException(status_code=404, detail="Proveedor no encontrado") from None
    except ProveedorConProductosError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None

"""Router de operaciones CRUD para el catálogo de Productos."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response

from ...application.use_cases.producto_use_cases import ProductoUseCases
from ...domain.exceptions import CodigoProductoDuplicado, ProductoNoEncontrado, ProveedorNoEncontrado
from ...infrastructure.repositories.sql_producto_repo import SqlProductoRepository
from ...infrastructure.repositories.sql_proveedor_repo import SqlProveedorRepository
from ..dependencies import SessionDep, UsuarioDep
from ..schemas.producto_schemas import ProductoActualizar, ProductoCrear, ProductoResponse

router = APIRouter(prefix="/productos", tags=["Productos"])
IdPath = Annotated[int, Path(gt=0, description="Identificador entero mayor que cero")]


def get_producto_use_cases(session: SessionDep) -> ProductoUseCases:
    """Fábrica de casos de uso de producto inyectando repositorios concretos."""
    prod_repo = SqlProductoRepository(session)
    prov_repo = SqlProveedorRepository(session)
    return ProductoUseCases(producto_repo=prod_repo, proveedor_repo=prov_repo)


@router.post("", response_model=ProductoResponse, status_code=201)
def crear(
    datos: ProductoCrear,
    usuario: UsuarioDep,
    use_cases: Annotated[ProductoUseCases, Depends(get_producto_use_cases)],
):
    """Crea un nuevo producto asociado a un proveedor del usuario actual."""
    try:
        return use_cases.crear(
            codigo=datos.codigo,
            nombre=datos.nombre,
            categoria=datos.categoria,
            precio_centavos=datos.precio_centavos,
            proveedor_id=datos.proveedor_id,
            propietario_id=usuario.id,
        )
    except ProveedorNoEncontrado as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except CodigoProductoDuplicado as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None


@router.get("", response_model=list[ProductoResponse])
def listar(
    usuario: UsuarioDep,
    use_cases: Annotated[ProductoUseCases, Depends(get_producto_use_cases)],
    q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    categoria: Annotated[str | None, Query(min_length=1, max_length=60)] = None,
    proveedor_id: Annotated[int | None, Query(gt=0)] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
):
    """Lista los productos del usuario autenticado con filtros opcionales y paginación."""
    return use_cases.listar(
        propietario_id=usuario.id,
        q=q,
        categoria=categoria,
        proveedor_id=proveedor_id,
        offset=offset,
        limite=limite,
    )


@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener(
    producto_id: IdPath,
    usuario: UsuarioDep,
    use_cases: Annotated[ProductoUseCases, Depends(get_producto_use_cases)],
):
    """Obtiene un producto propio por ID. Si no existe o es ajeno, responde 404."""
    try:
        return use_cases.obtener_por_id(producto_id=producto_id, propietario_id=usuario.id)
    except ProductoNoEncontrado:
        raise HTTPException(status_code=404, detail="Producto no encontrado") from None


@router.patch("/{producto_id}", response_model=ProductoResponse)
def actualizar(
    producto_id: IdPath,
    datos: ProductoActualizar,
    usuario: UsuarioDep,
    use_cases: Annotated[ProductoUseCases, Depends(get_producto_use_cases)],
):
    """Actualiza parcialmente un producto propio comprobando propiedad y unicidad."""
    try:
        return use_cases.actualizar(
            producto_id=producto_id,
            propietario_id=usuario.id,
            codigo=datos.codigo,
            nombre=datos.nombre,
            categoria=datos.categoria,
            precio_centavos=datos.precio_centavos,
            proveedor_id=datos.proveedor_id,
        )
    except ProductoNoEncontrado:
        raise HTTPException(status_code=404, detail="Producto no encontrado") from None
    except ProveedorNoEncontrado as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except CodigoProductoDuplicado as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None


@router.delete("/{producto_id}", status_code=204)
def eliminar(
    producto_id: IdPath,
    usuario: UsuarioDep,
    use_cases: Annotated[ProductoUseCases, Depends(get_producto_use_cases)],
):
    """Elimina un producto propio. Si no existe o es ajeno, responde 404."""
    try:
        use_cases.eliminar(producto_id=producto_id, propietario_id=usuario.id)
        return Response(status_code=204)
    except ProductoNoEncontrado:
        raise HTTPException(status_code=404, detail="Producto no encontrado") from None

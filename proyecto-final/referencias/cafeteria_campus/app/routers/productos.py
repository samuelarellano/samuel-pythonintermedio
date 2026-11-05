"""APIRouter agrupa operaciones; Depends comparte entradas y validaciones."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path

from app.datos import productos
from app.dependencias import parametros_busqueda
from app.modelos import ProductoCrear

# prefix forma parte de la URL; tags agrupa operaciones en /docs.
router = APIRouter(prefix="/productos", tags=["Productos"])


@router.get("")
def listar_productos(filtros: Annotated[dict, Depends(parametros_busqueda)]):
    resultados = productos
    if filtros["q"] is not None:
        resultados = [p for p in resultados if filtros["q"].lower() in p["nombre"].lower()]
    return resultados[:filtros["limite"]]


# Declarar esta ruta fija antes de /{producto_id} evita interpretar
# la palabra bebidas como un identificador entero.
@router.get("/bebidas")
def listar_bebidas(filtros: Annotated[dict, Depends(parametros_busqueda)]):
    resultados = [p for p in productos if p["categoria"] == "bebida"]
    if filtros["q"] is not None:
        resultados = [p for p in resultados if filtros["q"].lower() in p["nombre"].lower()]
    return resultados[:filtros["limite"]]


@router.get("/{producto_id}")
def obtener_producto(producto_id: Annotated[int, Path(gt=0)]):
    for producto in productos:
        if producto["id"] == producto_id:
            return producto
    raise HTTPException(status_code=404, detail="Producto no encontrado")


@router.post("", status_code=201)
def crear_producto(producto: ProductoCrear):
    nuevo_id = max((p["id"] for p in productos), default=0) + 1
    nuevo = {"id": nuevo_id, **producto.model_dump()}
    productos.append(nuevo)
    return nuevo

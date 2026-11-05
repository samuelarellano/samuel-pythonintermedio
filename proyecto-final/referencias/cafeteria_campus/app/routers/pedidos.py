"""Segundo router: crear y consultar pedidos de un solo producto."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path

from app.datos import pedidos, productos
from app.modelos import PedidoCrear

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("")
def listar_pedidos():
    return pedidos


@router.get("/{pedido_id}")
def obtener_pedido(pedido_id: Annotated[int, Path(gt=0)]):
    for pedido in pedidos:
        if pedido["id"] == pedido_id:
            return pedido
    raise HTTPException(status_code=404, detail="Pedido no encontrado")


@router.post("", status_code=201)
def crear_pedido(pedido: PedidoCrear):
    for producto in productos:
        if producto["id"] == pedido.producto_id:
            nuevo_id = max((p["id"] for p in pedidos), default=0) + 1
            nuevo = {
                "id": nuevo_id,
                **pedido.model_dump(),
                "total_centavos": producto["precio_centavos"] * pedido.cantidad,
            }
            pedidos.append(nuevo)
            return nuevo
    raise HTTPException(status_code=404, detail="Producto no encontrado")

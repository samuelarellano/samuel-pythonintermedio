"""Modelos del cuerpo JSON: el cliente no elige los ids ni el total."""

from pydantic import BaseModel, Field


class ProductoCrear(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    categoria: str = Field(min_length=1, max_length=40)
    precio_centavos: int = Field(gt=0, le=100000)


class PedidoCrear(BaseModel):
    producto_id: int = Field(gt=0)
    cantidad: int = Field(ge=1, le=20)

"""Ejecutar: python -m uvicorn demos.fundamentos:app --reload."""
from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Demo: contratos, routers y dependencias")
router = APIRouter(prefix="/objetos", tags=["Objetos"])


class Objeto(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)


def paginacion(limite: Annotated[int, Query(ge=1, le=20)] = 10):
    return limite


@router.get("")
def listar(limite: Annotated[int, Depends(paginacion)]):
    return [{"nombre": "Luna"}, {"nombre": "Saturno"}][:limite]


@router.post("", response_model=Objeto, status_code=201)
def mostrar_contrato(datos: Objeto):
    # ¿Se guarda? No: esta demo aísla la validación, no la persistencia.
    return datos


app.include_router(router)

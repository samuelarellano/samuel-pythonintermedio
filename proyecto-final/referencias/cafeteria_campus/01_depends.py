"""Etapa 1. Desde esta carpeta: python -m uvicorn 01_depends:app --reload."""

from typing import Annotated

from fastapi import Depends, FastAPI, Query

app = FastAPI(title="Cafetería: entender Depends")

productos = [
    {"id": 1, "nombre": "Café americano", "categoria": "bebida"},
    {"id": 2, "nombre": "Té de limón", "categoria": "bebida"},
    {"id": 3, "nombre": "Pan de elote", "categoria": "alimento"},
]


def parametros_busqueda(
    q: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    limite: Annotated[int, Query(ge=1, le=20)] = 10,
):
    # FastAPI obtiene estos valores de la consulta y los valida.
    # Esta función devuelve el valor que recibirán ambos endpoints.
    return {"q": q, "limite": limite}


@app.get("/")
def inicio():
    return {"mensaje": "Primero estudia Depends", "documentacion": "/docs"}


@app.get("/productos")
def listar_productos(filtros: Annotated[dict, Depends(parametros_busqueda)]):
    # Pasamos la función SIN paréntesis: FastAPI la ejecuta por petición.
    # filtros es su resultado; no es un parámetro JSON que envía el cliente.
    resultados = productos
    if filtros["q"] is not None:
        resultados = [p for p in resultados if filtros["q"].lower() in p["nombre"].lower()]
    return resultados[:filtros["limite"]]


@app.get("/bebidas")
def listar_bebidas(filtros: Annotated[dict, Depends(parametros_busqueda)]):
    # Reutilizamos la declaración y validación de q y limite.
    resultados = [p for p in productos if p["categoria"] == "bebida"]
    if filtros["q"] is not None:
        resultados = [p for p in resultados if filtros["q"].lower() in p["nombre"].lower()]
    return resultados[:filtros["limite"]]

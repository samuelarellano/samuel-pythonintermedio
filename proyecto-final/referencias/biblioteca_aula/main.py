"""API completa de referencia. Ejecutar desde esta carpeta con uvicorn."""

from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Biblioteca del aula", version="1.0.0")

# Se reinicia al detener o recargar el servidor. Usar un solo proceso.
libros = [
    {"id": 1, "titulo": "El principito", "autor": "Antoine de Saint-Exupéry", "paginas": 96},
    {"id": 2, "titulo": "Python para todos", "autor": "Raúl González", "paginas": 160},
    {"id": 3, "titulo": "Aprende Python", "autor": "Ana López", "paginas": 240},
]


class LibroCrear(BaseModel):
    # El cliente envía estos campos; el servidor asigna el id.
    titulo: str = Field(min_length=1, max_length=100)
    autor: str = Field(min_length=1, max_length=80)
    paginas: int = Field(gt=0, le=2000)


@app.get("/")
def inicio():
    return {"mensaje": "Bienvenido a la biblioteca del aula", "documentacion": "/docs"}


@app.get("/libros")
def listar_libros(
    q: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    limite: Annotated[int, Query(ge=1, le=20)] = 10,
):
    # q y limite son parámetros de consulta: /libros?q=python&limite=1
    resultados = libros
    if q is not None:
        resultados = [libro for libro in libros if q.lower() in libro["titulo"].lower()]
    return resultados[:limite]


@app.get("/libros/{libro_id}")
def obtener_libro(libro_id: Annotated[int, Path(gt=0)]):
    # libro_id es un parámetro de ruta: /libros/2
    for libro in libros:
        if libro["id"] == libro_id:
            return libro
    raise HTTPException(status_code=404, detail="Libro no encontrado")


@app.post("/libros", status_code=201)
def crear_libro(libro: LibroCrear):
    # FastAPI valida el cuerpo JSON antes de ejecutar esta función.
    nuevo_id = max((elemento["id"] for elemento in libros), default=0) + 1
    nuevo_libro = {"id": nuevo_id, **libro.model_dump()}
    libros.append(nuevo_libro)
    return nuevo_libro

"""Primero lee la parte guiada; después resuelve TODO 1 a TODO 4.

Ejecutar: python -m uvicorn practica:app --reload
"""

from typing import Annotated

from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field

app = FastAPI(title="Biblioteca del aula · práctica", version="1.0.0")

# PARTE GUIADA: estos datos simulan una biblioteca sin usar una base de datos.
libros = [
    {"id": 1, "titulo": "El principito", "autor": "Antoine de Saint-Exupéry", "paginas": 96},
    {"id": 2, "titulo": "Python para todos", "autor": "Raúl González", "paginas": 160},
    {"id": 3, "titulo": "Aprende Python", "autor": "Ana López", "paginas": 240},
]


class LibroCrear(BaseModel):
    # PARTE GUIADA: BaseModel describe el JSON que esperamos recibir.
    # Field agrega reglas: no basta con que titulo y autor sean cadenas.
    titulo: str = Field(min_length=1, max_length=100)
    autor: str = Field(min_length=1, max_length=80)
    # TODO 1: siguiendo los ejemplos anteriores, validar páginas entre 1 y 2000.
    paginas: int


@app.get("/")
def inicio():
    # PARTE GUIADA: el decorador conecta GET / con esta función.
    # El diccionario se convierte automáticamente en una respuesta JSON.
    return {"mensaje": "Bienvenido a la biblioteca del aula", "documentacion": "/docs"}


@app.get("/libros")
def listar_libros(
    # PARTE GUIADA: q llega desde la URL: /libros?q=python
    # None permite omitirlo; Query valida su longitud cuando sí se envía.
    q: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    limite: int = 10,
):
    resultados = libros
    if q is not None:
        resultados = []
        for libro in libros:
            if q.lower() in libro["titulo"].lower():
                resultados.append(libro)
    # TODO 2: validar limite entre 1 y 20 con Query y devolver solo esa cantidad.
    # TODO 2: validar limite entre 1 y 20 con Query y devolver solo esa cantidad.
    return resultados


# ACTIVIDAD: a partir de aquí, completa la lógica siguiendo EJERCICIOS.md.
@app.get("/libros/{libro_id}")
def obtener_libro(libro_id: Annotated[int, Path(gt=0)]):
    # TODO 3: buscar por id; devolver el libro o lanzar un error 404.
    raise HTTPException(status_code=501, detail="TODO 3: completar búsqueda por id")


@app.post("/libros", status_code=201)
def crear_libro(libro: LibroCrear):
    # TODO 4: generar id, convertir el modelo a diccionario, guardar y devolver.
    raise HTTPException(status_code=501, detail="TODO 4: completar creación de libros")

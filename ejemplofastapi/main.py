"""Ejemplo básico de una API construida con FastAPI."""

from fastapi import FastAPI

app = FastAPI(title="Ejemplo FastAPI", version="1.0.0")


@app.get("/lovers")
def listar_actividades_favoritas():
    """Devuelve una lista de actividades que me gusta realizar."""
    return [
        {"id": 1, "titulo": "Escuchar audiolibros"},
        {"id": 2, "titulo": "Aprender programación en Python"},
        {"id": 3, "titulo": "Salir a caminar y conocer lugares nuevos"},
    ]

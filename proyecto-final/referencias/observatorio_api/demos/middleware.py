"""Ejecutar: python -m uvicorn demos.middleware:app --reload."""
from time import perf_counter
from uuid import uuid4
from fastapi import FastAPI, HTTPException, Request

app = FastAPI(title="Demo: middleware")


@app.middleware("http")
async def medir(request: Request, call_next):
    inicio = perf_counter()
    request.state.identificador = uuid4().hex
    respuesta = await call_next(request)
    respuesta.headers["X-Request-ID"] = request.state.identificador
    respuesta.headers["X-Process-Time"] = f"{perf_counter() - inicio:.6f}"
    return respuesta


@app.get("/saludo")
def saludo(request: Request):
    return {"mensaje": "Cielo despejado", "id": request.state.identificador}


@app.get("/error")
def error():
    # ¿HTTPException atraviesa el middleware como respuesta? Sí, se convierte en 404.
    raise HTTPException(404, "Objeto no encontrado")

"""Etapa 2. Desde cafeteria_campus: python -m uvicorn app.main:app --reload."""

from fastapi import FastAPI

from app.routers import pedidos, productos

app = FastAPI(title="Cafetería del campus", version="1.0.0")

# Importar los módulos no registra sus rutas: hay que incluir los routers.
app.include_router(productos.router)
app.include_router(pedidos.router)


@app.get("/", tags=["Inicio"])
def inicio():
    return {"mensaje": "Bienvenido a la cafetería del campus", "documentacion": "/docs"}

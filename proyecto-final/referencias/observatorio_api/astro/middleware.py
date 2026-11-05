"""Observabilidad transversal sin registrar contraseñas ni Authorization."""
import logging
from time import perf_counter
from uuid import uuid4

from fastapi import Request

logger = logging.getLogger("uvicorn.error")


async def trazabilidad(request: Request, call_next):
    inicio = perf_counter()
    request.state.request_id = uuid4().hex
    response = await call_next(request)
    duracion = perf_counter() - inicio
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Process-Time"] = f"{duracion:.6f}"
    logger.info("request_id=%s method=%s status=%s seconds=%.6f",
                request.state.request_id, request.method, response.status_code, duracion)
    # ¿Mide la descarga completa? No: mide hasta obtener esta respuesta de call_next.
    return response

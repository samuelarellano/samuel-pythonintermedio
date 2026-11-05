"""Middleware transversal de observabilidad y trazabilidad HTTP.

Documentación de alcance y métricas:
- Qué mide realmente X-Process-Time:
  Mide el tiempo de procesamiento interno del servidor (CPU e I/O en base de datos)
  desde que la petición entra al middleware ASGI hasta que la función de ruta y dependencias
  producen la cabecera de la respuesta HTTP.
- Qué NO mide:
  No mide la latencia de red entre cliente y servidor, el tiempo de negociación TLS/TCP,
  ni la transferencia completa de streaming de cuerpos grandes a través del cable.
- Privacidad y seguridad en logs:
  Registra únicamente request_id, método, path, código de estado y duración.
  Está terminantemente prohibido registrar cabeceras de Authorization, cookies, contraseñas
  o cuerpos de petición.
"""
import logging
from time import perf_counter
from uuid import uuid4
from fastapi import Request, Response

logger = logging.getLogger("uvicorn.error")


async def trazabilidad_middleware(request: Request, call_next) -> Response:
    """Inyecta un identificador único X-Request-ID y la duración X-Process-Time en segundos."""
    inicio = perf_counter()
    request_id = uuid4().hex
    request.state.request_id = request_id

    try:
        response = await call_next(request)
        duracion = perf_counter() - inicio
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{duracion:.6f}"

        logger.info(
            "request_id=%s method=%s path=%s status=%s seconds=%.6f",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duracion,
        )
        return response
    except Exception as exc:
        duracion = perf_counter() - inicio
        logger.error(
            "request_id=%s method=%s path=%s error=%s seconds=%.6f",
            request_id,
            request.method,
            request.url.path,
            type(exc).__name__,
            duracion,
        )
        raise

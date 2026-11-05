"""La misma dependencia de la etapa 1, ahora en su propio módulo."""

from typing import Annotated

from fastapi import Query


def parametros_busqueda(
    q: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    limite: Annotated[int, Query(ge=1, le=20)] = 10,
):
    return {"q": q, "limite": limite}

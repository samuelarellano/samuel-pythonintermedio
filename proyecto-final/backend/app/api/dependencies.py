"""Dependencias comunes para inyección en FastAPI."""
from typing import Annotated
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session

from ..infrastructure.database import get_session
from ..infrastructure.models import UsuarioTable
from ..infrastructure.security import leer_token

SessionDep = Annotated[Session, Depends(get_session)]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def no_autorizado() -> HTTPException:
    """Error estándar 401 con cabecera WWW-Authenticate: Bearer obligatoria."""
    return HTTPException(
        status_code=401,
        detail="Credenciales no válidas",
        headers={"WWW-Authenticate": "Bearer"},
    )


def usuario_actual(
    request: Request,
    session: SessionDep,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> UsuarioTable:
    """Resuelve y valida la identidad del usuario a partir del token Bearer."""
    try:
        usuario_id = leer_token(token, request.app.state.settings)
    except (InvalidTokenError, ValueError, TypeError):
        raise no_autorizado() from None

    usuario = session.get(UsuarioTable, usuario_id)
    if usuario is None:
        raise no_autorizado()

    return usuario


UsuarioDep = Annotated[UsuarioTable, Depends(usuario_actual)]

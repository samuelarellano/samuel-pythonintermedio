"""FastAPI resuelve este grafo antes de ejecutar la operación de ruta."""
from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from sqlmodel import Session

from .database import get_session
from .models import Usuario
from .security import leer_token

SessionDep = Annotated[Session, Depends(get_session)]
oauth2 = OAuth2PasswordBearer(tokenUrl="auth/token")


def no_autorizado():
    return HTTPException(401, "Credenciales no válidas",
                         headers={"WWW-Authenticate": "Bearer"})


def usuario_actual(request: Request, session: SessionDep,
                   token: Annotated[str, Depends(oauth2)]) -> Usuario:
    try:
        usuario_id = leer_token(token, request.app.state.settings)
    except (InvalidTokenError, ValueError, TypeError):
        raise no_autorizado() from None
    usuario = session.get(Usuario, usuario_id)
    if usuario is None:
        raise no_autorizado()
    return usuario


UsuarioDep = Annotated[Usuario, Depends(usuario_actual)]
# ¿Dos Depends(get_session) crean dos sesiones? FastAPI reutiliza por petición.

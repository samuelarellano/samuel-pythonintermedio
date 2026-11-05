"""Registro público, login por formulario y perfil autenticado."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from ..dependencies import SessionDep, UsuarioDep, no_autorizado
from ..models import Usuario
from ..schemas import Registro, Token, UsuarioPublico
from ..security import DUMMY_HASH, crear_token, password_hash

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioPublico, status_code=201)
def registrar(datos: Registro, session: SessionDep):
    usuario = Usuario(username=datos.username, password_hash=password_hash.hash(datos.password))
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError:
        # ¿Consultar antes evita carreras? No; la restricción UNIQUE decide.
        session.rollback()
        raise HTTPException(409, "Nombre de usuario ocupado") from None
    session.refresh(usuario)
    return usuario


@router.post("/token", response_model=Token)
def login(request: Request, response: Response, session: SessionDep,
          form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    usuario = session.exec(select(Usuario).where(Usuario.username == form.username)).first()
    valido = password_hash.verify(form.password, usuario.password_hash if usuario else DUMMY_HASH)
    if not usuario or not valido:
        raise no_autorizado()
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return Token(access_token=crear_token(usuario.id, request.app.state.settings))


@router.get("/yo", response_model=UsuarioPublico)
def perfil(usuario: UsuarioDep):
    return usuario

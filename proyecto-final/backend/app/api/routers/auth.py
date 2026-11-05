"""Router de autenticación: registro, login OAuth2 y perfil actual."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select

from ..dependencies import SessionDep, UsuarioDep, no_autorizado
from ...infrastructure.models import UsuarioTable
from ...infrastructure.security import DUMMY_HASH, crear_token, password_hash
from ..schemas.auth_schemas import RegistroRequest, TokenResponse, UsuarioResponse

router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/registro", response_model=UsuarioResponse, status_code=201)
def registrar(datos: RegistroRequest, session: SessionDep):
    """Registra un nuevo usuario con contraseña cifrada mediante Argon2."""
    usuario = UsuarioTable(
        username=datos.username,
        password_hash=password_hash.hash(datos.password),
    )
    session.add(usuario)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=409, detail="Nombre de usuario ya ocupado") from None

    session.refresh(usuario)
    return usuario


@router.post("/token", response_model=TokenResponse)
def login(
    request: Request,
    response: Response,
    session: SessionDep,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """Autentica al usuario mediante formulario OAuth2 y emite un token Bearer."""
    usuario = session.exec(
        select(UsuarioTable).where(UsuarioTable.username == form.username)
    ).first()

    # Mitigación de timing attack: si el usuario no existe, se ejecuta verificación con DUMMY_HASH
    hash_a_verificar = usuario.password_hash if usuario else DUMMY_HASH
    credenciales_validas = password_hash.verify(form.password, hash_a_verificar)

    if not usuario or not credenciales_validas:
        raise no_autorizado()

    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"

    token = crear_token(usuario.id, request.app.state.settings)
    return TokenResponse(access_token=token)


@router.get("/yo", response_model=UsuarioResponse)
def perfil(usuario: UsuarioDep):
    """Devuelve el perfil público del usuario autenticado."""
    return usuario

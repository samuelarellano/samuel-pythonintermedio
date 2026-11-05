"""Hash unidireccional y JWT firmado cumplen funciones diferentes."""
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()
# Igualar el trabajo de hash cuando el usuario no existe evita una diferencia obvia.
DUMMY_HASH = password_hash.hash("usuario-inexistente-solo-para-comparar")


def crear_token(usuario_id: int, settings) -> str:
    ahora = datetime.now(timezone.utc)
    return jwt.encode(
        {"sub": str(usuario_id), "iat": ahora,
         "exp": ahora + timedelta(minutes=settings.token_minutes)},
        settings.jwt_secret, algorithm="HS256",
    )


def leer_token(token: str, settings) -> int:
    payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"],
                         options={"require": ["sub", "exp", "iat"]})
    # ¿El cliente decide el algoritmo? No, la lista permitida vive en el servidor.
    usuario_id = int(payload["sub"])
    if usuario_id <= 0:
        raise ValueError("Identificador inválido")
    return usuario_id

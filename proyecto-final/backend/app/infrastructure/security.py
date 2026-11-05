"""Criptografía de contraseñas con Argon2 y emisión/validación de tokens JWT."""
from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from .config import Settings

password_hash = PasswordHash.recommended()

# Hash estático precalculado para igualar el tiempo de cómputo ante usuarios inexistentes
DUMMY_HASH = password_hash.hash("usuario-inexistente-para-mitigar-timing-attacks")


def crear_token(usuario_id: int, settings: Settings) -> str:
    """Emite un token JWT con claims obligatorios: sub, iat y exp."""
    ahora = datetime.now(timezone.utc)
    expiracion = ahora + timedelta(minutes=settings.token_minutes)
    payload = {
        "sub": str(usuario_id),
        "iat": int(ahora.timestamp()),
        "exp": int(expiracion.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def leer_token(token: str, settings: Settings) -> int:
    """Valida y decodifica el token JWT exigiendo algoritmo HS256 y claims sub, iat y exp."""
    payload = jwt.decode(
        token,
        settings.jwt_secret,
        algorithms=["HS256"],
        options={"require": ["sub", "iat", "exp"]},
    )
    try:
        usuario_id = int(payload["sub"])
    except (ValueError, TypeError) as exc:
        raise ValueError("El sujeto (sub) del token no es un entero válido") from exc

    if usuario_id <= 0:
        raise ValueError("El identificador de usuario debe ser mayor que cero")

    return usuario_id

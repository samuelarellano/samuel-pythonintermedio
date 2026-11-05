"""Pruebas exhaustivas del módulo de autenticación, seguridad y tokens JWT."""
from datetime import datetime, timedelta, timezone
import jwt
import pytest
from fastapi.testclient import TestClient

from app.infrastructure.config import Settings

PASSWORD_VALIDO = "ContraseniaSegura2026!"


def registrar_usuario(client: TestClient, username: str = "usuario_test", password: str = PASSWORD_VALIDO):
    return client.post("/api/v1/auth/registro", json={"username": username, "password": password})


def login_usuario(client: TestClient, username: str = "usuario_test", password: str = PASSWORD_VALIDO):
    return client.post("/api/v1/auth/token", data={"username": username, "password": password})


def test_registro_valido_y_duplicado(client: TestClient):
    """Verifica registro exitoso (201) y rechazo con 409 ante username duplicado."""
    resp = registrar_usuario(client, "comerciante_1")
    assert resp.status_code == 201
    datos = resp.json()
    assert datos["username"] == "comerciante_1"
    assert "id" in datos
    assert "password_hash" not in datos
    assert "password" not in datos

    # Intento de duplicado
    resp_duplicado = registrar_usuario(client, "comerciante_1")
    assert resp_duplicado.status_code == 409
    assert "ya ocupado" in resp_duplicado.json()["detail"].lower()


@pytest.mark.parametrize("payload_invalido", [
    {"username": "ab", "password": PASSWORD_VALIDO},  # username < 3
    {"username": "UsuarioConMayusculas", "password": PASSWORD_VALIDO},  # no minúsculas
    {"username": "usuario con espacios", "password": PASSWORD_VALIDO},
    {"username": "usuario_valido", "password": "corta"},  # password < 12
    {"username": "usuario_valido", "password": PASSWORD_VALIDO, "extra_field": "inyeccion"},  # extra forbidden
])
def test_registro_validaciones_contrato_422(client: TestClient, payload_invalido):
    """Verifica que entradas inválidas son rechazadas con 422 Unprocessable Entity."""
    resp = client.post("/api/v1/auth/registro", json=payload_invalido)
    assert resp.status_code == 422


def test_login_exitoso_y_cabeceras_cache(client: TestClient):
    """Verifica login por formulario, token Bearer y Cache-Control: no-store."""
    registrar_usuario(client, "login_user")
    resp = login_usuario(client, "login_user")
    assert resp.status_code == 200
    datos = resp.json()
    assert "access_token" in datos
    assert datos["token_type"] == "bearer"
    assert resp.headers.get("Cache-Control") == "no-store"
    assert resp.headers.get("Pragma") == "no-cache"


def test_login_rechaza_credenciales_invalidas_y_usuario_inexistente(client: TestClient):
    """Verifica 401 y WWW-Authenticate: Bearer tanto para contraseña errónea como usuario inexistente."""
    registrar_usuario(client, "usuario_real")

    # Contraseña incorrecta
    resp_pass_mala = login_usuario(client, "usuario_real", "ContraseniaEquivocada123!")
    assert resp_pass_mala.status_code == 401
    assert "Bearer" in resp_pass_mala.headers.get("WWW-Authenticate", "")

    # Usuario inexistente (misma respuesta 401 para mitigar enumeración y timing attacks)
    resp_no_existe = login_usuario(client, "usuario_inexistente", PASSWORD_VALIDO)
    assert resp_no_existe.status_code == 401
    assert "Bearer" in resp_no_existe.headers.get("WWW-Authenticate", "")

    # Rechazo si se envía JSON en lugar de formulario urlencoded
    resp_json = client.post("/api/v1/auth/token", json={"username": "usuario_real", "password": PASSWORD_VALIDO})
    assert resp_json.status_code == 422


def test_perfil_con_y_sin_token(client: TestClient):
    """Verifica consulta de perfil en /api/v1/auth/yo con y sin token."""
    # Sin token
    resp_sin_token = client.get("/api/v1/auth/yo")
    assert resp_sin_token.status_code == 401
    assert "Bearer" in resp_sin_token.headers.get("WWW-Authenticate", "")

    # Con token válido
    registrar_usuario(client, "perfil_user")
    token = login_usuario(client, "perfil_user").json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    resp_con_token = client.get("/api/v1/auth/yo", headers=headers)
    assert resp_con_token.status_code == 200
    assert resp_con_token.json()["username"] == "perfil_user"
    assert "password_hash" not in resp_con_token.json()


def test_rechazo_tokens_vencidos_malformados_o_firmas_ajenas(client: TestClient, settings: Settings):
    """Verifica rechazo con 401 de tokens manipulados, vencidos o con claims faltantes."""
    ahora = datetime.now(timezone.utc)

    # 1. Token firmado con otra clave secreta
    token_otra_clave = jwt.encode(
        {"sub": "1", "iat": int(ahora.timestamp()), "exp": int((ahora + timedelta(minutes=10)).timestamp())},
        "clave_secreta_totalmente_distinta_y_ajena_1234567890",
        algorithm="HS256",
    )
    resp = client.get("/api/v1/auth/yo", headers={"Authorization": f"Bearer {token_otra_clave}"})
    assert resp.status_code == 401

    # 2. Token vencido
    token_vencido = jwt.encode(
        {"sub": "1", "iat": int((ahora - timedelta(minutes=30)).timestamp()), "exp": int((ahora - timedelta(minutes=10)).timestamp())},
        settings.jwt_secret,
        algorithm="HS256",
    )
    resp_vencido = client.get("/api/v1/auth/yo", headers={"Authorization": f"Bearer {token_vencido}"})
    assert resp_vencido.status_code == 401

    # 3. Token sin claim sub
    token_sin_sub = jwt.encode(
        {"iat": int(ahora.timestamp()), "exp": int((ahora + timedelta(minutes=10)).timestamp())},
        settings.jwt_secret,
        algorithm="HS256",
    )
    assert client.get("/api/v1/auth/yo", headers={"Authorization": f"Bearer {token_sin_sub}"}).status_code == 401

    # 4. Token sin claim exp
    token_sin_exp = jwt.encode(
        {"sub": "1", "iat": int(ahora.timestamp())},
        settings.jwt_secret,
        algorithm="HS256",
    )
    assert client.get("/api/v1/auth/yo", headers={"Authorization": f"Bearer {token_sin_exp}"}).status_code == 401

    # 5. Token sin claim iat
    token_sin_iat = jwt.encode(
        {"sub": "1", "exp": int((ahora + timedelta(minutes=10)).timestamp())},
        settings.jwt_secret,
        algorithm="HS256",
    )
    assert client.get("/api/v1/auth/yo", headers={"Authorization": f"Bearer {token_sin_iat}"}).status_code == 401

    # 6. Token con sub inválido (<= 0 o no entero)
    token_sub_cero = jwt.encode(
        {"sub": "0", "iat": int(ahora.timestamp()), "exp": int((ahora + timedelta(minutes=10)).timestamp())},
        settings.jwt_secret,
        algorithm="HS256",
    )
    assert client.get("/api/v1/auth/yo", headers={"Authorization": f"Bearer {token_sub_cero}"}).status_code == 401

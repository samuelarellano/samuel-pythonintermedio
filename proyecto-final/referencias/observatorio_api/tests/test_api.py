"""Especificación ejecutable resuelta. ¿Usa datos de clase? No: tmp_path aísla todo."""
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from astro.config import Settings
from astro.main import create_app

PASSWORD = "CieloDespejado2026!"


@pytest.fixture
def settings(tmp_path):
    return Settings(_env_file=None, jwt_secret="a" * 64,
                    database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}")


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        yield client


def registrar(client, username="luna"):
    return client.post("/auth/registro", json={"username": username, "password": PASSWORD})


def autenticar(client, username="luna"):
    registrar(client, username)
    respuesta = client.post("/auth/token", data={"username": username, "password": PASSWORD})
    assert respuesta.status_code == 200
    assert respuesta.headers["Cache-Control"] == "no-store"
    return {"Authorization": "Bearer " + respuesta.json()["access_token"]}


def crear(client, headers, objeto="Saturno"):
    return client.post("/observaciones", headers=headers,
                       json={"objeto": objeto, "notas": "Anillos visibles"})


def test_registro_contrato_duplicado_y_login(client):
    respuesta = registrar(client)
    assert respuesta.status_code == 201
    assert set(respuesta.json()) == {"id", "username"}
    assert registrar(client).status_code == 409
    assert client.post("/auth/token", data={"username": "luna", "password": "incorrecta"}).status_code == 401
    assert client.post("/auth/token", data={"username": "nadie", "password": PASSWORD}).status_code == 401
    assert client.post("/auth/token", json={"username": "luna", "password": PASSWORD}).status_code == 422


def test_crud_completo_y_validacion(client):
    headers = autenticar(client)
    assert client.get("/auth/yo", headers=headers).json()["username"] == "luna"
    respuesta = crear(client, headers)
    assert respuesta.status_code == 201
    ruta = f"/observaciones/{respuesta.json()['id']}"
    assert client.get(ruta, headers=headers).json()["objeto"] == "Saturno"
    assert client.patch(ruta, headers=headers, json={"notas": "Noche clara"}).json()["objeto"] == "Saturno"
    assert client.patch(ruta, headers=headers, json={"notas": None}).status_code == 422
    assert client.post("/observaciones", headers=headers,
                       json={"objeto": " ", "notas": "x"}).status_code == 422
    assert client.post("/observaciones", headers=headers,
                       json={"objeto": "Luna", "notas": "x", "propietario_id": 99}).status_code == 422
    assert client.get("/observaciones?limite=0", headers=headers).status_code == 422
    assert client.get("/observaciones/0", headers=headers).status_code == 422
    assert client.get("/observaciones/99999", headers=headers).status_code == 404
    assert client.delete(ruta, headers=headers).status_code == 204
    assert client.get(ruta, headers=headers).status_code == 404


def test_propiedad_en_todas_las_operaciones(client):
    ana = autenticar(client, "ana")
    sol = autenticar(client, "sol")
    ruta = f"/observaciones/{crear(client, ana).json()['id']}"
    assert client.get("/observaciones", headers=sol).json() == []
    assert client.get(ruta, headers=sol).status_code == 404
    assert client.patch(ruta, headers=sol, json={"objeto": "Luna"}).status_code == 404
    assert client.delete(ruta, headers=sol).status_code == 404
    assert client.get(ruta, headers=ana).status_code == 200


@pytest.mark.parametrize("caso", ["vencido", "otra_clave", "sin_exp", "sujeto_invalido", "usuario_ausente"])
def test_rechaza_tokens(client, settings, caso):
    registrar(client)
    ahora = datetime.now(timezone.utc)
    payload = {"sub": "1", "iat": ahora, "exp": ahora + timedelta(minutes=5)}
    clave = settings.jwt_secret
    if caso == "vencido":
        payload["exp"] = ahora - timedelta(seconds=5)
    elif caso == "otra_clave":
        clave = "b" * 64
    elif caso == "sin_exp":
        del payload["exp"]
    elif caso == "sujeto_invalido":
        payload["sub"] = "no-es-id"
    else:
        payload["sub"] = "9999"
    token = jwt.encode(payload, clave, algorithm="HS256")
    respuesta = client.get("/auth/yo", headers={"Authorization": f"Bearer {token}"})
    assert respuesta.status_code == 401
    assert respuesta.headers["WWW-Authenticate"] == "Bearer"


def test_sin_token_middleware_y_cors(client):
    respuesta = client.get("/observaciones")
    assert respuesta.status_code == 401
    assert len(respuesta.headers["X-Request-ID"]) == 32
    assert float(respuesta.headers["X-Process-Time"]) >= 0
    respuesta = client.options("/observaciones", headers={"Origin": "http://localhost:5173",
                                "Access-Control-Request-Method": "POST"})
    assert respuesta.status_code == 200
    assert respuesta.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert client.options("/observaciones", headers={"Origin": "https://ajeno.example",
                           "Access-Control-Request-Method": "POST"}).status_code == 400


def test_filtro_paginacion_y_literal_sql(client):
    headers = autenticar(client)
    crear(client, headers, "Saturno")
    crear(client, headers, "Luna")
    assert len(client.get("/observaciones?q=Sat", headers=headers).json()) == 1
    assert client.get("/observaciones?offset=1&limite=1", headers=headers).json()[0]["objeto"] == "Luna"
    assert client.get("/observaciones?q=%25", headers=headers).json() == []


def test_persistencia_al_reabrir(settings):
    with TestClient(create_app(settings)) as primero:
        headers = autenticar(primero)
        crear(primero, headers)
    with TestClient(create_app(settings)) as segundo:
        assert segundo.get("/observaciones", headers=headers).json()[0]["objeto"] == "Saturno"


def test_config_rechaza_marcador():
    with pytest.raises(ValidationError):
        Settings(_env_file=None, jwt_secret="REEMPLAZAR_POR_UN_SECRETO_ALEATORIO_DE_64_CARACTERES")

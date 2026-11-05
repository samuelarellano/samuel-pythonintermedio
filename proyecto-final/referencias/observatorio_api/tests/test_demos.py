"""Cada demo se comprueba de forma independiente de astro."""
from fastapi.testclient import TestClient


def test_fundamentos():
    from demos.fundamentos import app
    with TestClient(app) as client:
        assert len(client.get("/objetos?limite=1").json()) == 1
        assert client.get("/objetos?limite=0").status_code == 422


def test_middleware():
    from demos.middleware import app
    with TestClient(app) as client:
        respuesta = client.get("/saludo")
        assert respuesta.json()["id"] == respuesta.headers["X-Request-ID"]
        assert "X-Process-Time" in client.get("/error").headers


def test_sqlite(tmp_path, monkeypatch):
    from demos import sqlite
    from sqlmodel import create_engine
    engine = create_engine(f"sqlite:///{(tmp_path / 'demo.db').as_posix()}",
                           connect_args={"check_same_thread": False})
    monkeypatch.setattr(sqlite, "engine", engine)
    with TestClient(sqlite.app) as client:
        respuesta = client.post("/objetos", json={"nombre": "Luna"})
        assert respuesta.status_code == 201
        ruta = f"/objetos/{respuesta.json()['id']}"
        assert client.get(ruta).json()["nombre"] == "Luna"
        assert client.put(ruta, json={"nombre": "Saturno"}).json()["nombre"] == "Saturno"
        assert len(client.get("/objetos").json()) == 1
        assert client.delete(ruta).status_code == 204
        assert client.get(ruta).status_code == 404


def test_oauth2():
    from demos.oauth2_jwt import app
    with TestClient(app) as client:
        assert client.get("/yo").status_code == 401
        assert client.post("/token", data={"username": "luna", "password": "mal"}).status_code == 401
        respuesta = client.post("/token", data={"username": "luna", "password": "CieloDespejado2026!"})
        token = respuesta.json()["access_token"]
        assert client.get("/yo", headers={"Authorization": f"Bearer {token}"}).json() == {"username": "luna"}

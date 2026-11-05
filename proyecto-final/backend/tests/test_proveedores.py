"""Pruebas del CRUD de Proveedores, aislamiento multiusuario y persistencia."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.infrastructure.config import Settings
from app.main import create_app

PASSWORD = "ContraseniaSegura2026!"


def auth_header(client: TestClient, username: str) -> dict[str, str]:
    """Registra y autentica un usuario, retornando el header Authorization: Bearer."""
    client.post("/api/v1/auth/registro", json={"username": username, "password": PASSWORD})
    resp = client.post("/api/v1/auth/token", data={"username": username, "password": PASSWORD})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_crud_proveedor_completo(client: TestClient):
    """Verifica el flujo completo de creación, consulta, listado, patch y eliminación."""
    headers = auth_header(client, "comerciante_crud")

    # 1. Crear proveedor (POST)
    payload = {
        "nombre": "Distribuidora del Norte",
        "contacto": "Carlos Mendoza",
        "telefono": "555-123-4567",
    }
    resp_crear = client.post("/api/v1/proveedores", headers=headers, json=payload)
    assert resp_crear.status_code == 201
    datos = resp_crear.json()
    assert datos["nombre"] == "Distribuidora del Norte"
    assert datos["contacto"] == "Carlos Mendoza"
    assert datos["telefono"] == "555-123-4567"
    assert "id" in datos
    assert "propietario_id" not in datos
    prov_id = datos["id"]

    # 2. Consultar por ID (GET)
    resp_get = client.get(f"/api/v1/proveedores/{prov_id}", headers=headers)
    assert resp_get.status_code == 200
    assert resp_get.json()["id"] == prov_id

    # 3. Listar con paginación y filtro q (GET)
    resp_lista = client.get("/api/v1/proveedores?q=Norte&offset=0&limite=10", headers=headers)
    assert resp_lista.status_code == 200
    assert len(resp_lista.json()) == 1
    assert resp_lista.json()[0]["id"] == prov_id

    # 4. Actualizar con PATCH
    resp_patch = client.patch(
        f"/api/v1/proveedores/{prov_id}",
        headers=headers,
        json={"telefono": "555-999-8888"},
    )
    assert resp_patch.status_code == 200
    assert resp_patch.json()["telefono"] == "555-999-8888"
    assert resp_patch.json()["nombre"] == "Distribuidora del Norte"  # Omitido conservado

    # 5. Eliminar (DELETE)
    resp_delete = client.delete(f"/api/v1/proveedores/{prov_id}", headers=headers)
    assert resp_delete.status_code == 204

    # 6. Comprobar que ya no existe (404)
    assert client.get(f"/api/v1/proveedores/{prov_id}", headers=headers).status_code == 404


def test_aislamiento_estricto_entre_dos_usuarios(client: TestClient):
    """Prueba de seguridad: Usuario B no puede listar, consultar, editar ni borrar datos de Usuario A."""
    headers_a = auth_header(client, "usuario_a")
    headers_b = auth_header(client, "usuario_b")

    # Usuario A crea un proveedor
    resp_a = client.post(
        "/api/v1/proveedores",
        headers=headers_a,
        json={"nombre": "Proveedor Privado A", "contacto": "Contacto A", "telefono": "111-222-3333"},
    )
    assert resp_a.status_code == 201
    id_a = resp_a.json()["id"]

    # 1. Usuario B no ve el proveedor en su lista
    resp_lista_b = client.get("/api/v1/proveedores", headers=headers_b)
    assert resp_lista_b.status_code == 200
    assert resp_lista_b.json() == []

    # 2. Usuario B recibe 404 al intentar consultar el ID de A
    assert client.get(f"/api/v1/proveedores/{id_a}", headers=headers_b).status_code == 404

    # 3. Usuario B recibe 404 al intentar actualizar el ID de A
    resp_patch_b = client.patch(
        f"/api/v1/proveedores/{id_a}",
        headers=headers_b,
        json={"nombre": "Intento de Hackeo"},
    )
    assert resp_patch_b.status_code == 404

    # 4. Usuario B recibe 404 al intentar eliminar el ID de A
    assert client.delete(f"/api/v1/proveedores/{id_a}", headers=headers_b).status_code == 404

    # Confirmar que los datos de Usuario A siguen intactos
    resp_intacto = client.get(f"/api/v1/proveedores/{id_a}", headers=headers_a)
    assert resp_intacto.status_code == 200
    assert resp_intacto.json()["nombre"] == "Proveedor Privado A"


def test_rechazo_asignar_propietario_o_id_desde_cliente(client: TestClient):
    """El cliente no puede asignar id ni propietario_id (extra='forbid')."""
    headers = auth_header(client, "comerciante_seguro")

    # Inyección de propietario_id en creación
    resp_prop = client.post(
        "/api/v1/proveedores",
        headers=headers,
        json={"nombre": "Test", "contacto": "Test", "telefono": "12345678", "propietario_id": 999},
    )
    assert resp_prop.status_code == 422

    # Inyección de id en creación
    resp_id = client.post(
        "/api/v1/proveedores",
        headers=headers,
        json={"nombre": "Test", "contacto": "Test", "telefono": "12345678", "id": 1},
    )
    assert resp_id.status_code == 422


def test_validaciones_de_texto_y_anti_null_en_patch(client: TestClient):
    """Comprueba que campos vacíos y null explícito en PATCH son rechazados sin mutar datos."""
    headers = auth_header(client, "comerciante_validador")

    # Cadenas vacías o con solo espacios son rechazadas
    assert client.post(
        "/api/v1/proveedores",
        headers=headers,
        json={"nombre": "   ", "contacto": "Valido", "telefono": "12345678"},
    ).status_code == 422

    # Teléfono menor a 7 caracteres
    assert client.post(
        "/api/v1/proveedores",
        headers=headers,
        json={"nombre": "Valido", "contacto": "Valido", "telefono": "123"},
    ).status_code == 422

    # Crear uno válido
    creado = client.post(
        "/api/v1/proveedores",
        headers=headers,
        json={"nombre": "Original", "contacto": "Original", "telefono": "12345678"},
    ).json()

    # Enviar null explícito en PATCH devuelve 422
    resp_null = client.patch(
        f"/api/v1/proveedores/{creado['id']}",
        headers=headers,
        json={"nombre": None},
    )
    assert resp_null.status_code == 422

    # ID menor o igual a 0 da 422
    assert client.get("/api/v1/proveedores/0", headers=headers).status_code == 422


def test_persistencia_sobrevive_reinicio_servidor(settings: Settings):
    """Comprueba que los datos creados sobreviven al cerrar la app y reabrirla contra la misma BD."""
    # Primer ciclo de vida
    with TestClient(create_app(settings)) as client_1:
        headers = auth_header(client_1, "persistencia_user")
        resp = client_1.post(
            "/api/v1/proveedores",
            headers=headers,
            json={"nombre": "Persistente", "contacto": "Ana", "telefono": "555-123-9999"},
        )
        assert resp.status_code == 201
        prov_id = resp.json()["id"]

    # Segundo ciclo de vida (nueva instancia con la misma base)
    with TestClient(create_app(settings)) as client_2:
        # Autenticar nuevamente al mismo usuario existente
        login_resp = client_2.post("/api/v1/auth/token", data={"username": "persistencia_user", "password": PASSWORD})
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers_reinicio = {"Authorization": f"Bearer {token}"}

        # Consultar proveedor previamente guardado
        resp_reinicio = client_2.get(f"/api/v1/proveedores/{prov_id}", headers=headers_reinicio)
        assert resp_reinicio.status_code == 200
        assert resp_reinicio.json()["nombre"] == "Persistente"

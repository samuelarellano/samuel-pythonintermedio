"""Pruebas del CRUD de Productos, validación cruzada con proveedores, unicidad e integridad."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from app.infrastructure.config import Settings
from app.main import create_app

PASSWORD = "ContraseniaSegura2026!"


def auth_header(client: TestClient, username: str) -> dict[str, str]:
    """Registra y autentica un usuario, retornando la cabecera Bearer."""
    client.post("/api/v1/auth/registro", json={"username": username, "password": PASSWORD})
    resp = client.post("/api/v1/auth/token", data={"username": username, "password": PASSWORD})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def crear_proveedor(client: TestClient, headers: dict[str, str], nombre: str = "Proveedor Base") -> int:
    """Helper para crear un proveedor válido y retornar su ID."""
    resp = client.post(
        "/api/v1/proveedores",
        headers=headers,
        json={"nombre": nombre, "contacto": "Contacto", "telefono": "12345678"},
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_crud_producto_completo(client: TestClient):
    """Verifica el flujo CRUD completo de productos con precios en centavos enteros."""
    headers = auth_header(client, "user_crud_prod")
    prov_id = crear_proveedor(client, headers, "Proveedor Central")

    # 1. Crear producto (POST)
    payload = {
        "codigo": "CAFE-01",
        "nombre": "Café de Altura 500g",
        "categoria": "Bebidas",
        "precio_centavos": 14500,  # $145.00 MXN
        "proveedor_id": prov_id,
    }
    resp_crear = client.post("/api/v1/productos", headers=headers, json=payload)
    assert resp_crear.status_code == 201
    datos = resp_crear.json()
    assert datos["codigo"] == "CAFE-01"
    assert datos["precio_centavos"] == 14500
    assert datos["proveedor_id"] == prov_id
    assert "propietario_id" not in datos
    prod_id = datos["id"]

    # 2. Consultar por ID (GET)
    resp_get = client.get(f"/api/v1/productos/{prod_id}", headers=headers)
    assert resp_get.status_code == 200
    assert resp_get.json()["id"] == prod_id

    # 3. Listar con filtros
    resp_lista = client.get(f"/api/v1/productos?q=Altura&categoria=Bebidas&proveedor_id={prov_id}", headers=headers)
    assert resp_lista.status_code == 200
    assert len(resp_lista.json()) == 1
    assert resp_lista.json()[0]["id"] == prod_id

    # 4. Actualizar con PATCH
    resp_patch = client.patch(
        f"/api/v1/productos/{prod_id}",
        headers=headers,
        json={"precio_centavos": 15000, "nombre": "Café de Altura Tostado 500g"},
    )
    assert resp_patch.status_code == 200
    assert resp_patch.json()["precio_centavos"] == 15000
    assert resp_patch.json()["codigo"] == "CAFE-01"  # Campo omitido conservado

    # 5. Eliminar (DELETE)
    resp_delete = client.delete(f"/api/v1/productos/{prod_id}", headers=headers)
    assert resp_delete.status_code == 204

    # 6. Comprobar que no existe (404)
    assert client.get(f"/api/v1/productos/{prod_id}", headers=headers).status_code == 404


def test_unicidad_codigo_por_usuario(client: TestClient):
    """Mismo usuario no puede duplicar código (409), pero dos usuarios distintos sí pueden."""
    headers_a = auth_header(client, "user_codigo_a")
    headers_b = auth_header(client, "user_codigo_b")

    prov_a = crear_proveedor(client, headers_a, "Prov A")
    prov_b = crear_proveedor(client, headers_b, "Prov B")

    payload_a1 = {
        "codigo": "SKU-SHARED",
        "nombre": "Producto User A",
        "categoria": "General",
        "precio_centavos": 2000,
        "proveedor_id": prov_a,
    }
    assert client.post("/api/v1/productos", headers=headers_a, json=payload_a1).status_code == 201

    # Intento de duplicar en el mismo usuario A -> 409 Conflict
    payload_a2 = {
        "codigo": "SKU-SHARED",
        "nombre": "Otro Producto User A",
        "categoria": "General",
        "precio_centavos": 3000,
        "proveedor_id": prov_a,
    }
    resp_dup = client.post("/api/v1/productos", headers=headers_a, json=payload_a2)
    assert resp_dup.status_code == 409
    assert "ya registrado" in resp_dup.json()["detail"].lower()

    # Usuario B usa el mismo código bajo su propio catálogo -> 201 Created exitoso
    payload_b = {
        "codigo": "SKU-SHARED",
        "nombre": "Producto User B",
        "categoria": "General",
        "precio_centavos": 5000,
        "proveedor_id": prov_b,
    }
    assert client.post("/api/v1/productos", headers=headers_b, json=payload_b).status_code == 201


def test_proveedor_inexistente_o_ajeno_responde_404(client: TestClient):
    """Asociar un producto a un proveedor ajeno o inexistente se rechaza con 404 Not Found."""
    headers_a = auth_header(client, "user_rel_a")
    headers_b = auth_header(client, "user_rel_b")

    prov_a = crear_proveedor(client, headers_a, "Prov de A")

    # Usuario B intenta asociar su producto al proveedor de A
    payload_ajeno = {
        "codigo": "PROD-B",
        "nombre": "Producto B",
        "categoria": "General",
        "precio_centavos": 1000,
        "proveedor_id": prov_a,
    }
    resp_ajeno = client.post("/api/v1/productos", headers=headers_b, json=payload_ajeno)
    assert resp_ajeno.status_code == 404
    assert "no encontrado" in resp_ajeno.json()["detail"].lower()

    # Proveedor inexistente (ID 99999)
    payload_inexistente = {
        "codigo": "PROD-B",
        "nombre": "Producto B",
        "categoria": "General",
        "precio_centavos": 1000,
        "proveedor_id": 99999,
    }
    assert client.post("/api/v1/productos", headers=headers_b, json=payload_inexistente).status_code == 404


def test_impedir_eliminacion_proveedor_con_productos_409(client: TestClient):
    """Regla de integridad: No se puede eliminar un proveedor que tenga productos asociados."""
    headers = auth_header(client, "user_delete_check")
    prov_id = crear_proveedor(client, headers, "Proveedor Con Dependencias")

    # Asociar producto al proveedor
    resp_prod = client.post(
        "/api/v1/productos",
        headers=headers,
        json={
            "codigo": "DEP-01",
            "nombre": "Producto Dependiente",
            "categoria": "Test",
            "precio_centavos": 5000,
            "proveedor_id": prov_id,
        },
    )
    assert resp_prod.status_code == 201
    prod_id = resp_prod.json()["id"]

    # Intentar eliminar el proveedor con productos -> 409 Conflict
    resp_del_prov = client.delete(f"/api/v1/proveedores/{prov_id}", headers=headers)
    assert resp_del_prov.status_code == 409
    assert "productos asociados" in resp_del_prov.json()["detail"].lower()

    # Confirmar que el proveedor sigue existiendo
    assert client.get(f"/api/v1/proveedores/{prov_id}", headers=headers).status_code == 200

    # Eliminar primero el producto dependiente (204)
    assert client.delete(f"/api/v1/productos/{prod_id}", headers=headers).status_code == 204

    # Ahora sí se puede eliminar el proveedor limpiamente (204)
    assert client.delete(f"/api/v1/proveedores/{prov_id}", headers=headers).status_code == 204


def test_ausencia_acceso_cruzado_productos(client: TestClient):
    """Usuario B no puede acceder, modificar ni borrar productos de Usuario A."""
    headers_a = auth_header(client, "user_iso_a")
    headers_b = auth_header(client, "user_iso_b")

    prov_a = crear_proveedor(client, headers_a, "Prov A")
    prod_a_id = client.post(
        "/api/v1/productos",
        headers=headers_a,
        json={"codigo": "ISO-A", "nombre": "Prod A", "categoria": "A", "precio_centavos": 100, "proveedor_id": prov_a},
    ).json()["id"]

    # Usuario B consulta GET/{id_de_A} -> 404
    assert client.get(f"/api/v1/productos/{prod_a_id}", headers=headers_b).status_code == 404

    # Usuario B intenta PATCH -> 404
    assert client.patch(f"/api/v1/productos/{prod_a_id}", headers=headers_b, json={"nombre": "Hack"}).status_code == 404

    # Usuario B intenta DELETE -> 404
    assert client.delete(f"/api/v1/productos/{prod_a_id}", headers=headers_b).status_code == 404

    # Usuario B lista productos -> lista vacía
    assert client.get("/api/v1/productos", headers=headers_b).json() == []


def test_persistencia_relacion_sobrevive_reinicio(settings: Settings):
    """Comprueba que la relación producto-proveedor persiste intacta entre reinicios del servidor."""
    with TestClient(create_app(settings)) as client_1:
        headers = auth_header(client_1, "persistencia_rel_user")
        prov_id = crear_proveedor(client_1, headers, "Proveedor Relacional")
        resp_prod = client_1.post(
            "/api/v1/productos",
            headers=headers,
            json={
                "codigo": "PERSIST-REL",
                "nombre": "Harina de Maíz",
                "categoria": "Abarrotes",
                "precio_centavos": 2350,
                "proveedor_id": prov_id,
            },
        )
        assert resp_prod.status_code == 201
        prod_id = resp_prod.json()["id"]

    # Nueva instancia con el mismo archivo de base de datos
    with TestClient(create_app(settings)) as client_2:
        token = client_2.post(
            "/api/v1/auth/token",
            data={"username": "persistencia_rel_user", "password": PASSWORD},
        ).json()["access_token"]
        headers_reinicio = {"Authorization": f"Bearer {token}"}

        resp = client_2.get(f"/api/v1/productos/{prod_id}", headers=headers_reinicio)
        assert resp.status_code == 200
        assert resp.json()["nombre"] == "Harina de Maíz"
        assert resp.json()["precio_centavos"] == 2350
        assert resp.json()["proveedor_id"] == prov_id


def test_validaciones_precio_centavos_y_anti_null(client: TestClient):
    """Comprueba rechazo de precios <= 0, cadenas vacías y null en PATCH."""
    headers = auth_header(client, "user_val_prod")
    prov_id = crear_proveedor(client, headers, "Prov Val")

    # Precio <= 0 da 422
    assert client.post(
        "/api/v1/productos",
        headers=headers,
        json={"codigo": "V01", "nombre": "N", "categoria": "C", "precio_centavos": 0, "proveedor_id": prov_id},
    ).status_code == 422

    # Inyección de propietario_id da 422
    assert client.post(
        "/api/v1/productos",
        headers=headers,
        json={"codigo": "V01", "nombre": "N", "categoria": "C", "precio_centavos": 100, "proveedor_id": prov_id, "propietario_id": 99},
    ).status_code == 422

    # Crear válido
    prod_id = client.post(
        "/api/v1/productos",
        headers=headers,
        json={"codigo": "V01", "nombre": "N", "categoria": "C", "precio_centavos": 100, "proveedor_id": prov_id},
    ).json()["id"]

    # null explícito en PATCH da 422
    assert client.patch(
        f"/api/v1/productos/{prod_id}",
        headers=headers,
        json={"precio_centavos": None},
    ).status_code == 422

"""Pruebas de observabilidad (middleware), CORS, paginación, orden y escape de comodines SQL."""
import pytest
from fastapi.testclient import TestClient

PASSWORD = "ContraseniaSegura2026!"


def auth_header(client: TestClient, username: str) -> dict[str, str]:
    client.post("/api/v1/auth/registro", json={"username": username, "password": PASSWORD})
    resp = client.post("/api/v1/auth/token", data={"username": username, "password": PASSWORD})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_middleware_headers_en_exito_y_errores(client: TestClient):
    """Verifica que X-Request-ID y X-Process-Time se inyectan en 200, 401, 404 y 422."""
    # 1. Éxito 200
    resp_200 = client.get("/salud")
    assert resp_200.status_code == 200
    assert "X-Request-ID" in resp_200.headers
    assert "X-Process-Time" in resp_200.headers
    assert float(resp_200.headers["X-Process-Time"]) >= 0

    # 2. Error 401 (sin token)
    resp_401 = client.get("/api/v1/auth/yo")
    assert resp_401.status_code == 401
    assert "X-Request-ID" in resp_401.headers
    assert "X-Process-Time" in resp_401.headers

    # 3. Error 422 (contrato inválido)
    resp_422 = client.post("/api/v1/auth/registro", json={"username": "ab"})
    assert resp_422.status_code == 422
    assert "X-Request-ID" in resp_422.headers
    assert "X-Process-Time" in resp_422.headers

    # 4. Error 404 (recurso no encontrado)
    headers = auth_header(client, "user_trazabilidad_404")
    resp_404 = client.get("/api/v1/proveedores/99999", headers=headers)
    assert resp_404.status_code == 404
    assert "X-Request-ID" in resp_404.headers
    assert "X-Process-Time" in resp_404.headers


def test_cors_preflight_y_exposicion_cabeceras(client: TestClient):
    """Comprueba que OPTIONS preflight responde con origen permitido y cabeceras expuestas."""
    cabeceras_preflight = {
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Authorization, Content-Type",
    }
    resp = client.options("/api/v1/productos", headers=cabeceras_preflight)
    assert resp.status_code == 200
    assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"
    assert "POST" in resp.headers.get("access-control-allow-methods", "")

    # Petición GET normal con Origin debe exponer las cabeceras de trazabilidad
    resp_get = client.get("/salud", headers={"Origin": "http://localhost:5173"})
    assert resp_get.headers.get("access-control-allow-origin") == "http://localhost:5173"
    expuestas = resp_get.headers.get("access-control-expose-headers", "")
    assert "X-Request-ID" in expuestas
    assert "X-Process-Time" in expuestas


def test_busqueda_literal_con_comodines_sql_autoescape(client: TestClient):
    """Verifica que caracteres % y _ se buscan literalmente sin actuar como comodines SQL."""
    headers = auth_header(client, "user_wildcards")

    # Crear dos proveedores: uno con '%' en el nombre y otro sin él
    p1 = client.post("/api/v1/proveedores", headers=headers, json={
        "nombre": "Frutas 100% Frescas", "contacto": "A", "telefono": "12345678"
    }).json()
    p2 = client.post("/api/v1/proveedores", headers=headers, json={
        "nombre": "Frutas 100 Grados", "contacto": "B", "telefono": "12345678"
    }).json()

    # Búsqueda con "100%" debe retornar solo p1 (no p2)
    resp_porcentaje = client.get("/api/v1/proveedores?q=100%", headers=headers)
    assert resp_porcentaje.status_code == 200
    ids_encontrados = [p["id"] for p in resp_porcentaje.json()]
    assert p1["id"] in ids_encontrados
    assert p2["id"] not in ids_encontrados

    # Crear dos productos: uno con guion bajo '_' y otro con guion medio '-'
    prov_id = p1["id"]
    prod_guion_bajo = client.post("/api/v1/productos", headers=headers, json={
        "codigo": "ITEM_01", "nombre": "Producto Con Guion Bajo", "categoria": "C", "precio_centavos": 100, "proveedor_id": prov_id
    }).json()
    prod_guion_medio = client.post("/api/v1/productos", headers=headers, json={
        "codigo": "ITEM-01", "nombre": "Producto Con Guion Medio", "categoria": "C", "precio_centavos": 100, "proveedor_id": prov_id
    }).json()

    # Búsqueda con "ITEM_" debe retornar solo prod_guion_bajo (el '_' no debe hacer match con '-')
    resp_guion = client.get("/api/v1/productos?q=ITEM_", headers=headers)
    assert resp_guion.status_code == 200
    ids_prods = [p["id"] for p in resp_guion.json()]
    assert prod_guion_bajo["id"] in ids_prods
    assert prod_guion_medio["id"] not in ids_prods


def test_paginacion_orden_estable_y_validacion_limites(client: TestClient):
    """Comprueba paginación secuencial, orden determinista por ID y validación 422 de límites."""
    headers = auth_header(client, "user_pagination")
    prov_id = client.post("/api/v1/proveedores", headers=headers, json={
        "nombre": "Proveedor Paginado", "contacto": "X", "telefono": "12345678"
    }).json()["id"]

    # Crear 5 productos
    creados = []
    for i in range(1, 6):
        res = client.post("/api/v1/productos", headers=headers, json={
            "codigo": f"PAGE-{i:02d}",
            "nombre": f"Producto Paginado {i}",
            "categoria": "Paginacion",
            "precio_centavos": i * 1000,
            "proveedor_id": prov_id,
        }).json()
        creados.append(res["id"])

    # Página 1: offset=0, limite=2 -> primeros 2 ordenados por ID ascendente
    p1 = client.get(f"/api/v1/productos?categoria=Paginacion&offset=0&limite=2", headers=headers).json()
    assert [p["id"] for p in p1] == creados[0:2]

    # Página 2: offset=2, limite=2 -> siguientes 2
    p2 = client.get(f"/api/v1/productos?categoria=Paginacion&offset=2&limite=2", headers=headers).json()
    assert [p["id"] for p in p2] == creados[2:4]

    # Página 3: offset=4, limite=2 -> el último
    p3 = client.get(f"/api/v1/productos?categoria=Paginacion&offset=4&limite=2", headers=headers).json()
    assert [p["id"] for p in p3] == creados[4:5]

    # Offset más allá del final devuelve lista vacía [] (200)
    p_vacio = client.get(f"/api/v1/productos?categoria=Paginacion&offset=10&limite=2", headers=headers).json()
    assert p_vacio == []

    # Validaciones de límites (422)
    assert client.get("/api/v1/productos?limite=0", headers=headers).status_code == 422
    assert client.get("/api/v1/productos?limite=101", headers=headers).status_code == 422
    assert client.get("/api/v1/productos?offset=-1", headers=headers).status_code == 422


def test_filtro_no_amplia_acceso_fuera_del_catalogo(client: TestClient):
    """Comprueba que filtrar por un proveedor ajeno nunca revela productos ajenos."""
    headers_a = auth_header(client, "user_filter_a")
    headers_b = auth_header(client, "user_filter_b")

    prov_a = client.post("/api/v1/proveedores", headers=headers_a, json={
        "nombre": "Prov A", "contacto": "A", "telefono": "12345678"
    }).json()["id"]

    client.post("/api/v1/productos", headers=headers_a, json={
        "codigo": "SEC-A", "nombre": "Secreto de A", "categoria": "Privado", "precio_centavos": 9999, "proveedor_id": prov_a
    })

    # Usuario B consulta filtrando con el proveedor_id de A -> lista vacía
    resp = client.get(f"/api/v1/productos?proveedor_id={prov_a}", headers=headers_b)
    assert resp.status_code == 200
    assert resp.json() == []

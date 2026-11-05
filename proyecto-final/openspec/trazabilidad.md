# Matriz de Trazabilidad Educativa y Técnica: La Estrellita
`openspec/trazabilidad.md`
Versión: 1.1.0 | Alineada con `openspec/specs/catalogo-la-estrellita.md`

Esta matriz vincula de forma explícita y bidireccional los conceptos enseñados por el profesor Emmanuel Pulido con las especificaciones funcionales, modelos mínimos y verificaciones automatizadas de **La Estrellita**.

---

| Código | Tema del Curso / Referencia | Origen | Requisito SDD / Funcionalidad | Verificación Ejecutable Planificada |
|---|---|---|---|---|
| **T01** | Routing básico, verbos HTTP (GET, POST, PATCH, DELETE) y códigos de estado (200, 201, 204, 404, 409, 422) | `biblioteca_aula` | `REQ-PROV-01` a `06`, `REQ-PROD-01` a `06` en routers modulares | Pruebas de integración con `TestClient` validando código de estado y payload exacto por cada ruta. |
| **T02** | Validación de tipos, restricciones (`Path`, `Query`, `Field`) y error 422 con localización de fallo | `biblioteca_aula` | Parámetros de ruta `Id = Annotated[int, Path(gt=0)]`, query params con límites en `schemas.py` | Pruebas parametrizadas en pytest enviando datos inválidos (cadenas en IDs numéricos, límites < 1 o > 100). |
| **T03** | Modelos Pydantic v2, validación estricta (`extra="forbid"`) y anti-null en actualizaciones parciales | `observatorio_api` (`schemas.py`) | `ProveedorCrear`, `ProveedorActualizar`, `ProductoCrear`, `ProductoActualizar` | Tests enviando campos desconocidos (esperando 422) y tests enviando `{"nombre": null}` en PATCH (esperando 422). |
| **T04** | Modularización con `APIRouter`, prefijos y etiquetas OpenAPI | `cafeteria_campus` (`app/routers/`) | Routers `auth.py`, `proveedores.py`, `productos.py`, `salud.py` | Comprobación de `/openapi.json` verificando etiquetas ("Autenticación", "Proveedores", "Productos", "Sistema"). |
| **T05** | Inyección de dependencias con `Depends` para validación y sesión de DB | `cafeteria_campus` (`dependencias.py`) y `observatorio_api` | Dependencias `SessionDep` y `UsuarioDep` inyectadas en operaciones | Pruebas asegurando que los routers reciben la sesión y el usuario decodificado del token. |
| **T06** | Cantidades monetarias en centavos enteros (`precio_centavos: int > 0`) | `cafeteria_campus` (`modelos.py`) | Modelo `Producto.precio_centavos` (validado con `gt=0`) y formateador frontend | Tests unitarios rechazando precios <= 0 o con decimales; verificación de formateo visual en pesos ($ MXN). |
| **T07** | Persistencia relacional con SQLModel y motor SQLite | `observatorio_api` (`astro/models.py`) | Tablas `Usuario`, `Proveedor`, `Producto` en `models.py` | Tests de ciclo de vida completo (crear, consultar, actualizar, borrar) en SQLite temporal. |
| **T08** | Activación de foreign keys en SQLite (`PRAGMA foreign_keys=ON`) y restricciones de unicidad compuestas | `observatorio_api` (`astro/database.py`) | Foreign keys en `Proveedor` y `Producto`, y `UniqueConstraint("propietario_id", "codigo")` | Test intentando crear producto con `proveedor_id` ajeno (404) y test de códigos duplicados en el mismo usuario (409). |
| **T09** | Application Factory (`create_app`) y ciclo de vida asíncrono (`lifespan`) | `observatorio_api` (`astro/main.py`) | Fábrica `create_app` en `main.py` con `create_all` y `engine.dispose()` | Test arrancando la aplicación mediante la fábrica con configuraciones aisladas de test sin efectos residuales. |
| **T10** | Configuración tipada con `pydantic-settings`, lectura de `.env` y validación de variables | `observatorio_api` (`astro/config.py`) | Clase `Settings` en `config.py` con validación de `jwt_secret` | Tests unitarios asegurando que secretos por defecto ("REEMPLAZAR...") son rechazados al iniciar. |
| **T11** | Middleware de observabilidad y trazabilidad HTTP (`X-Request-ID`, `X-Process-Time`) | `observatorio_api` (`astro/middleware.py`) | Middleware ASGI en `middleware.py` | Test con cliente HTTP comprobando presencia de cabeceras UUID y tiempos en respuestas exitosas y de error. |
| **T12** | Seguridad, autenticación OAuth2 y tokens JWT con hash Argon2 | `observatorio_api` (`astro/security.py`, `auth.py`) | Endpoints `POST /auth/registro`, `POST /auth/token`, `GET /auth/yo` | Tests de registro con contraseña segura, login con credenciales correctas/incorrectas y rechazo con 401. |
| **T13** | Aislamiento y comprobación estricta de propiedad (multi-tenant privado) | `observatorio_api` (`routers/observaciones.py`) | Verificación `propietario_id == usuario.id` en todas las operaciones | Test con dos cuentas ("usuario_a" y "usuario_b") confirmando que "usuario_b" recibe 404 al intentar acceder a datos de "a". |
| **T14** | Protección de integridad de negocio (Rechazo 409 al borrar proveedor con productos) | Requisito específico del proyecto final | Endpoint `DELETE /proveedores/{id}` validando inexistencia de productos | Test intentando borrar un proveedor con productos vinculados, comprobando respuesta 409 y preservación en DB. |
| **T15** | Accesibilidad web (WCAG 2.1 AA) e interacción por teclado y lector NVDA | Requisito específico del proyecto final | Frontend en React + TypeScript con HTML semántico, etiquetas ARIA y foco visible | Verificación manual con NVDA en Windows, navegación 100% por teclado y auditoría de accesibilidad. |

---

## Cobertura Pedagógica Garantizada
Cada ejercicio y patrón visto en clase se traslada a una necesidad funcional concreta de **La Estrellita**, garantizando una defensa del proyecto fluida y técnicamente justificada.

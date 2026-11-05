# Auditoría SDD Integral de Cobertura Académica: La Estrellita
`openspec/auditoria-academica.md`
Fecha: 4 de noviembre de 2026 | Versión: 1.0.0 | Metodología: SDD (Gentle Shell / el Gentleman)
Auditor: el Gentleman (Arquitecto de Software y Harness SDD)

---

## 1. Declaración de Alcance, Fuentes y Criterio de Auditoría

> ⚠️ **Declaración de Criterio y Ausencia de Rúbrica Oficial:**
> No existe en el repositorio una rúbrica formalmente publicada para la evaluación del proyecto final.
> Esta auditoría **comprueba la cobertura técnica, la conexión arquitectónica y el correcto funcionamiento** de los conceptos, patrones y buenas prácticas presentes en los materiales, guías didácticas, ejercicios y pruebas resueltas del profesor **Emmanuel Pulido**.
> El resultado de esta auditoría certifica el cumplimiento riguroso de los temas disponibles en el curso, pero **no garantiza una calificación académica específica**, la cual queda a exclusivo criterio del docente.

### 1.1. Localización y Estado de los Proyectos de Referencia
Las referencias no se encontraban bajo `referencias/curso`, sino en la raíz de `referencias/` dentro de `proyecto-final/`:
1. `referencias/biblioteca_aula/`: Fundamentos de HTTP, tipos, parámetros (`Path`, `Query`, `Field`), Pydantic v2, errores 404 vs 422 y pruebas unitarias aisladas con `TestClient`.
2. `referencias/cafeteria_campus/`: Modularización con `APIRouter`, inyección de dependencias compartidas con `Depends`, relaciones entre recursos y manejo de dinero exacto mediante enteros en centavos (`precio_centavos`).
3. `referencias/observatorio_api/`: Bitácora astronómica completa con arquitectura profesional: Application Factory (`create_app`), ciclo de vida asíncrono (`lifespan`), persistencia con SQLModel/SQLite con claves foráneas obligatorias (`PRAGMA foreign_keys=ON`), middleware ASGI de observabilidad (`X-Request-ID`, `X-Process-Time`), CORS configurado, configuración tipada (`pydantic-settings`), autenticación OAuth2 con tokens JWT (PyJWT), hashing Argon2 (`pwdlib`) con mitigación de timing attacks (`DUMMY_HASH`) y propiedad estricta de recursos.

**Estado de conservación:** Los tres proyectos de referencia permanecen **100% intactos e inalterados**.

---

## 2. Clasificación de Alcance (Los 4 Niveles de Criterio)

Para evitar confundir requisitos obligatorios con menciones didácticas o mejoras futuras, se clasifica cada aspecto en cuatro niveles:

### Nivel 1: Temas Demostrados en Clase y Resueltos en Referencias
Patrones y conceptos que el docente explicó mediante código completamente funcional y probado:
- Application Factory (`create_app`) y ciclo de vida (`lifespan`).
- Separación de esquemas HTTP (`schemas.py`) y tablas de base de datos (`models.py`).
- Activación forzosa de claves foráneas en SQLite mediante evento SQLAlchemy.
- Inyección de dependencias por petición con `yield` en `get_session`.
- Hashing Argon2 con `pwdlib` y mitigación de timing attacks con `DUMMY_HASH`.
- Emisión y validación estricta de JWT con PyJWT (algoritmo del servidor `HS256`, claims `sub`, `iat`, `exp`).
- Control de propiedad en todas las operaciones privadas (responder 404 ante recursos ajenos).
- Middleware de trazabilidad con `X-Request-ID` y `X-Process-Time`.
- Pruebas automatizadas en bases temporales efímeras con `tmp_path`.

### Nivel 2: Requisitos Explícitos de las Actividades y Ejercicios
Instrucciones obligatorias presentes en `EJERCICIOS.md` y `GUIA_DE_REPASO.md`:
- Distinción entre parámetros de ruta (`Path`), de consulta (`Query`) y cuerpo JSON (`Field`).
- Filtrado antes de paginar (`q` y `limite`).
- Diferenciación clara entre error de validación (422) y recurso no encontrado (404).
- Manejo monetario sin tipos flotantes (`precio_centavos: int > 0`).
- Agrupación por recursos con `APIRouter(prefix=..., tags=...)`.
- Declaración de rutas fijas antes de rutas dinámicas parametrizadas.

### Nivel 3: Ampliaciones Propias de La Estrellita
Características implementadas para elevar el proyecto a nivel de entrega final integral:
- Arquitectura limpia en **monolito modular** (`domain`, `application`, `infrastructure`, `api`, `main.py`).
- Dominio puro desacoplado: cero dependencias de FastAPI o SQLModel en entidades.
- Relación relacional completa: Proveedor 1 ──< N Producto.
- Restricción de unicidad compuesta en base de datos: `UniqueConstraint("propietario_id", "codigo")`.
- Regla de integridad de negocio: **Impedir eliminación de un proveedor que tenga productos asociados (409 Conflict)**.
- Búsqueda literal con `autoescape=True` en SQLAlchemy para evitar que `%` y `_` actúen como comodines accidentales.
- Frontend SPA accesible en **React 18 + TypeScript + Vite**.
- Cumplimiento **WCAG 2.1 AA** y optimización para lector de pantalla **NVDA** (Skip Link, foco visible, regiones vivas `role="status"` y `aria-live`, modales con focus trap y devolución de foco).
- Token JWT estrictamente en memoria en React para máxima seguridad contra XSS.
- Conversión decimal determinista a centavos en cliente (`pesosACentavos`) para evitar imprecisiones de coma flotante.
- Mitigación de condiciones de carrera en interfaz web mediante contador secuencial de peticiones.

### Nivel 4: Mejoras Futuras Mencionadas pero no Implementadas
Conceptos que las guías del docente citan como evolución hacia criterio profesional pero no forman parte del código ejecutable del curso:
- Migraciones de esquema versionadas con Alembic (las referencias usan `create_all`).
- Base de datos cliente-servidor (PostgreSQL) para concurrencia masiva.
- *Refresh tokens*, listas de revocación o sesiones persistentes en base de datos.
- Proveedor de identidad federado (OIDC / SSO).
- Rate limiting y protección contra ataques de fuerza bruta.
- Paginación por cursor y control de concurrencia optimista (ETags).

---

## 3. Revisión Detallada por Ejes Técnicos

### Eje A: Fundamentos y Validación
- **Métodos, rutas y decoradores:** Implementados mediante `@router.post`, `@router.get`, `@router.patch` y `@router.delete` en `routers/auth.py`, `routers/proveedores.py` y `routers/productos.py`.
- **Fuentes de entrada:**
  - Parámetros de ruta: `IdPath = Annotated[int, Path(gt=0)]`.
  - Parámetros de consulta: `q = Annotated[str | None, Query(min_length=1, max_length=100)]`, `offset = Annotated[int, Query(ge=0)]`, `limite = Annotated[int, Query(ge=1, le=100)]`.
  - Cuerpo JSON: Esquemas Pydantic v2 validados.
- **Diferencia entre 422 y 404:**
  - Si un cliente envía `/api/v1/proveedores/abc` o `?limite=0`, FastAPI responde `422 Unprocessable Entity` antes de ejecutar la función.
  - Si un cliente envía `/api/v1/proveedores/9999` (formato válido pero inexistente o ajeno), la aplicación responde `404 Not Found`.
- **Esquemas separados:** `ProveedorCrear` y `ProveedorActualizar` para entrada; `ProveedorResponse` para salida. En salida nunca se exponen claves foráneas de propiedad (`propietario_id`) ni secretos.
- **Rechazo de campos inesperados:** Configurado mediante `ConfigDict(extra="forbid", str_strip_whitespace=True)` en todos los esquemas de entrada. Enviar `propietario_id` o `id` desde el cliente es rechazado con 422.
- **Limpieza de textos sin alterar contraseñas:** Los esquemas de dominio aplican `str_strip_whitespace=True`. En contraste, en `RegistroRequest` la contraseña se mantiene intacta para respetar espacios intencionales elegidos por el usuario.
- **Semántica PATCH estricta:** `ProveedorActualizar` y `ProductoActualizar` usan validador `@field_validator(..., mode="before" / estándar)` que rechaza explícitamente `null` con 422 (*"Omite el campo si no quieres modificarlo"*), mientras que omitir el campo conserva su valor actual.

### Eje B: Depends e Inyección de Dependencias
- **Uso real en endpoints:** Todos los routers consumen `SessionDep = Annotated[Session, Depends(get_session)]` y `UsuarioDep = Annotated[UsuarioTable, Depends(usuario_actual)]`.
- **Ciclo de vida y cierre mediante `yield`:** `get_session` abre una `Session(engine)` y realiza `yield`. Al concluir la petición, el contexto se cierra de forma determinista.
- **Reutilización por petición:** FastAPI resuelve el grafo de dependencias reutilizando la misma sesión para autenticar y para la operación de base de datos.
- **Ausencia de sesiones globales:** El engine es compartido (`app.state.engine`), pero cada petición HTTP obtiene una instancia fresca y efímera de `Session`.
- **Composición de casos de uso:** Las fábricas de dependencias `get_proveedor_use_cases` y `get_producto_use_cases` instancian los repositorios y casos de uso inyectando la sesión activa.
- **Explicación didáctica:** En una llamada normal de Python, `def f(s: Session = Depends(...))` no ejecuta la dependencia; es el contenedor IoC de FastAPI quien interpreta el árbol de dependencias antes de invocar la función de ruta.

### Eje C: Organización de FastAPI
- **APIRouter, prefijos y tags:** Routers organizados en `api/routers/` con prefijos `/auth`, `/proveedores` y `/productos` y etiquetas para Swagger UI.
- **Inclusión centralizada:** Montados bajo el prefijo unificado `/api/v1` en `main.py`.
- **Rutas fijas vs. dinámicas:** No hay colisiones de rutas; el endpoint público `/salud` vive en la raíz (`/salud`) fuera de `/api/v1`.
- **Application Factory y Lifespan:** `create_app(settings)` permite inyectar configuraciones aisladas en pruebas. El `lifespan` asíncrono ejecuta `SQLModel.metadata.create_all(engine)` al arrancar y `engine.dispose()` al cerrar.
- **Configuración tipada:** `Settings(BaseSettings)` lee `.env`, valida longitudes y rechaza marcadores de ejemplo `"REEMPLAZAR..."`.

### Eje D: Middleware y CORS
- **Middleware ASGI de Trazabilidad:** Registrado en `main.py` mediante `app.middleware("http")(trazabilidad_middleware)`.
- **Cabeceras obligatorias:** Inyecta `X-Request-ID` (UUID4) y `X-Process-Time` (duración en segundos con 6 decimales) en cada respuesta HTTP (200, 401, 404, 422).
- **Seguridad en logging:** Registra método, path, código y tiempo; nunca registra cabeceras `Authorization`, contraseñas ni cuerpos.
- **Alcance real de la medición:** Mide el tiempo de cómputo e I/O interno del servidor desde que el request entra al middleware hasta que `call_next` entrega la cabecera de respuesta. No mide latencia física en el cable ni streaming de red.
- **CORS configurado y expuesto:** `CORSMiddleware` admite el origen de React (`http://localhost:5173`), métodos `["GET", "POST", "PATCH", "DELETE", "OPTIONS"]`, cabeceras `["Authorization", "Content-Type"]` y expone `expose_headers=["X-Request-ID", "X-Process-Time"]`.
- **Distinción CORS vs. Autenticación:** Se documenta que un preflight CORS exitoso solo autoriza al navegador a emitir la petición cruzada, pero no sustituye ni otorga autorización Bearer.

### Eje E: Base de Datos
- **Persistencia SQLModel con SQLite:** Modelos `UsuarioTable`, `ProveedorTable` y `ProductoTable` persistidos en archivo SQLite local.
- **Activación de Claves Foráneas:** SQLite ignora claves foráneas por defecto. Se activa forzosamente en cada conexión mediante:
  ```python
  @event.listens_for(engine, "connect")
  def activar_foreign_keys(connection, _):
      connection.execute("PRAGMA foreign_keys=ON")
  ```
- **Integridad referencial y unicidad:**
  - `ProductoTable.proveedor_id` referencia `proveedores.id`.
  - Restricción compuesta `UniqueConstraint("propietario_id", "codigo")` respaldada por motor SQL.
- **Búsqueda literal y paginación:** Repositorios usan `contains(q, autoescape=True)` para escapar `%` y `_`, aplicando el filtro antes de `.offset()` y `.limit()`, con orden estable `order_by(Table.id.asc())`.
- **Transacciones y Rollback:**
  - Creación de usuarios y productos captura `IntegrityError` y ejecuta `session.rollback()` antes de lanzar `HTTPException(409)`.
  - **Impedir eliminación de proveedor con productos:** La regla de negocio valida dependencias y responde `409 Conflict`.
- **Representación monetaria exacta:** Los precios se almacenan estrictamente como enteros en centavos (`precio_centavos: int > 0`), prohibiendo tipos `float`.
- **Estrategia de esquema:** Se documenta formalmente que `create_all` no migra tablas existentes.

### Eje F: Autenticación y Autorización
- **Argon2:** Cifrado unidireccional con `pwdlib.PasswordHash.recommended()`.
- **Mitigación de Timing Attacks:** Uso de `DUMMY_HASH` para usuarios inexistentes, igualando el tiempo de cómputo con un usuario real.
- **Login OAuth2:** Endpoint `/api/v1/auth/token` recibe formulario `application/x-www-form-urlencoded` con `OAuth2PasswordRequestForm` y emite `Cache-Control: no-store`.
- **Firma y Claims de JWT:** Firma `HS256` definida por el servidor; validación obligatoria de `sub`, `iat` y `exp` en `leer_token`.
- **Rechazo 401 con WWW-Authenticate:** Tokens vencidos, alterados o sin claims devuelven 401 con cabecera `WWW-Authenticate: Bearer`.
- **Control estricto de propiedad:**
  - `where(Table.propietario_id == usuario.id)` aplicado en todas las consultas.
  - Imposibilidad del cliente de establecer o cambiar propietario (rechazo 422).
  - Imposibilidad de vincular productos a proveedores ajenos (rechazo 404).

---

## 4. Auditoría de Accesibilidad (WCAG 2.1 AA / NVDA)

| Criterio | Estado | Evidencia de Implementación |
|---|---|---|
| **HTML Semántico** | Conforme | Uso de `<header>`, `<nav>`, `<main id="contenido-principal">`, `<footer>`, `<table>`, `<caption>`, `<th scope="col">`. |
| **Navegación por Teclado** | Conforme | Todos los elementos interactivos son operables con `Tab`, `Shift+Tab`, `Enter` y `Espacio`. Enlace Skip Link presente al inicio del DOM. |
| **Foco Visible** | Conforme | Regla CSS `:focus-visible` con contorno de alto contraste (naranja `#ea580c`, ratio > 3:1). |
| **Formularios Accesibles** | Conforme | Cada input cuenta con `<label htmlFor="...">` explícito, `aria-required`, `aria-invalid` y textos de ayuda asociados vía `aria-describedby`. |
| **Manejo de Foco en Modales** | Conforme | Los modales dirigen el foco al primer campo al abrirse, se cierran con `Escape` y devuelven el foco exactamente al botón disparador. En eliminación, el foco inicial se sitúa en "Cancelar" por seguridad. |
| **Lectores de Pantalla (NVDA)** | Conforme | Regiones vivas `role="status"` y `aria-live="polite"` anuncian resultados y cambios de vista sin desviar el foco del usuario. |

---

## 5. Dictamen Final de la Auditoría

- **Requisitos del Curso Demostrados:** **100% de los temas de clase** presentes en `biblioteca_aula`, `cafeteria_campus` y `observatorio_api` se encuentran implementados, conectados y respaldados por pruebas automatizadas.
- **Pruebas Automatizadas:** **30 pruebas pasando al 100%** en pytest sin fallos ni dependencias residuales en la base de datos de desarrollo.
- **Calidad de Código y Tipos:** Cero errores en `tsc --noEmit`, paquete de producción generado limpiamente con `vite build` y estricta separación de capas de arquitectura limpia.
- **Conclusión:** La Estrellita constituye una demostración técnica integral, sólida y pedagógicamente coherente con el programa de Python Intermedio.

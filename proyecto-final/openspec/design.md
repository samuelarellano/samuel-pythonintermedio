# Documento de Diseño Arquitectónico: Monolito Modular La Estrellita
`openspec/design.md`
Versión: 1.0.0 | Estado: Aprobado para implementación | Metodología: SDD (Gentle Shell / el Gentleman)

---

## 1. Visión y Topología de Carpetas

Se diseña una arquitectura limpia y proporcional orientada al dominio dentro de un monolito modular para backend y una arquitectura por features en frontend.

### 1.1. Estructura de Directorios

```
proyecto-final/
├── backend/
│   ├── app/
│   │   ├── domain/               # Entidades de negocio puras, reglas de invariantes y excepciones de dominio
│   │   │   ├── __init__.py
│   │   │   ├── exceptions.py     # EntidadNoEncontrada, ConflictoNegocio, ReglaInvalida
│   │   │   ├── usuario.py        # Entidad Usuario
│   │   │   ├── proveedor.py      # Entidad Proveedor
│   │   │   └── producto.py       # Entidad Producto
│   │   ├── application/          # Casos de uso y contratos de infraestructura (Interfaces/Protocols)
│   │   │   ├── __init__.py
│   │   │   ├── interfaces/       # Contratos de repositorios y servicios de seguridad
│   │   │   │   ├── repositorios.py  # IUsuarioRepo, IProveedorRepo, IProductoRepo, IUnitOfWork
│   │   │   │   └── seguridad.py     # IPasswordHasher, ITokenService
│   │   │   └── use_cases/        # Orquestación de casos de uso (login, crud proveedores, crud productos)
│   │   │       ├── auth_use_cases.py
│   │   │       ├── proveedor_use_cases.py
│   │   │       └── producto_use_cases.py
│   │   ├── infrastructure/       # Implementaciones concretas con SQLModel, SQLite, PyJWT y pwdlib
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # Settings con pydantic-settings
│   │   │   ├── database.py       # Engine SQLite, event foreign_keys=ON, get_session
│   │   │   ├── models.py         # Tablas SQLModel persistentes (UsuarioTable, etc.)
│   │   │   ├── repositories/     # Implementación concreta de los repositorios y UnitOfWork
│   │   │   │   ├── sql_usuario_repo.py
│   │   │   │   ├── sql_proveedor_repo.py
│   │   │   │   ├── sql_producto_repo.py
│   │   │   │   └── unit_of_work.py
│   │   │   ├── security.py       # Implementación concreta con Argon2 (pwdlib) y JWT (PyJWT)
│   │   │   └── middleware.py     # Trazabilidad ASGI (X-Request-ID, X-Process-Time)
│   │   ├── api/                  # Capa HTTP (FastAPI, Schemas Pydantic, Routers, Dependencias)
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py   # Inyección de SessionDep, UsuarioDep, UseCaseDep
│   │   │   ├── error_handlers.py # Mapeo de excepciones de dominio a HTTPException (404, 409, etc.)
│   │   │   ├── schemas/          # Contratos HTTP de entrada y salida con Pydantic v2
│   │   │   │   ├── auth_schemas.py
│   │   │   │   ├── proveedor_schemas.py
│   │   │   │   └── producto_schemas.py
│   │   │   └── routers/          # Endpoints REST bajo /api/v1
│   │   │       ├── auth.py
│   │   │       ├── proveedores.py
│   │   │       └── productos.py
│   │   └── main.py               # Composition Root: create_app(settings) y lifespan
│   ├── tests/                    # Pruebas automatizadas con pytest y tmp_path
│   │   ├── conftest.py
│   │   ├── test_auth.py
│   │   ├── test_proveedores.py
│   │   ├── test_productos.py
│   │   └── test_trazabilidad.py
│   ├── requirements.txt
│   └── requirements-dev.txt
│
└── frontend/
    ├── src/
    │   ├── features/             # Módulos organizados por dominio funcional
    │   │   ├── auth/             # Login, registro, estado de sesión en memoria
    │   │   │   ├── components/   # LoginForm, RegisterForm
    │   │   │   ├── hooks/        # useAuth
    │   │   │   └── types/        # AuthUser, Credentials, AuthTokens
    │   │   ├── proveedores/      # Vistas y componentes del catálogo de proveedores
    │   │   │   ├── components/   # ProveedorTable, ProveedorFormModal, ProveedorFiltros
    │   │   │   ├── hooks/        # useProveedores
    │   │   │   └── types/        # Proveedor
    │   │   └── productos/        # Vistas y componentes del catálogo de productos
    │   │       ├── components/   # ProductoTable, ProductoFormModal, ProductoFiltros
    │   │       ├── hooks/        # useProductos
    │   │       └── types/        # Producto
    │   ├── shared/               # Componentes, utilidades y configuración compartida
    │   │   ├── api/              # Cliente HTTP centralizado (fetch tipado, interceptor de token en memoria)
    │   │   │   └── client.ts
    │   │   ├── components/       # Componentes visuales accesibles reutilizables (Botón, Modal, Alerta, CampoTexto)
    │   │   │   ├── Button.tsx
    │   │   │   ├── TextField.tsx
    │   │   │   ├── Modal.tsx
    │   │   │   └── Alert.tsx
    │   │   └── utils/            # Formateadores (moneda MXN a partir de centavos) y helpers a11y
    │   │       ├── currency.ts
    │   │       └── a11y.ts
    │   ├── App.tsx
    │   └── main.tsx
    ├── index.html
    ├── package.json
    ├── tsconfig.json
    └── vite.config.ts
```

---

## 2. Reglas de Aislamiento y Responsabilidades por Capa

| Capa | Responsabilidad | Dependencias Permitidas | Prohibiciones Estrictas |
|---|---|---|---|
| **Domain** | Entidades de negocio, invariantes y excepciones de dominio. | Python estándar (`dataclasses`, `typing`, `re`). | **Prohibido importar FastAPI, Pydantic, SQLModel o SQLAlchemy.** |
| **Application** | Casos de uso y contratos de puertos (`Protocols`/`ABCs`). Coordina la lógica de negocio y delimita transacciones. | Capa Domain. Python estándar. | No conoce frameworks web ni detalles directos de motor SQL. |
| **Infrastructure** | Adaptadores concretos: SQLModel, SQLite síncrono, hashing Argon2 (`pwdlib`), JWT (`PyJWT`), configuración (`pydantic-settings`). | Capa Domain y Application. `sqlmodel`, `sqlalchemy`, `pydantic-settings`, `pwdlib`, `jwt`. | No debe filtrar objetos de sesión ni tablas SQLModel hacia la capa de API o de Dominio. |
| **API** | Capa HTTP: endpoints FastAPI, validación de entrada/salida Pydantic v2, inyección de dependencias, mapeo de excepciones a respuestas HTTP. | Capa Application y Domain. `fastapi`, `pydantic`. | No ejecuta consultas directas a la base de datos; delega en casos de uso. |
| **main.py** | Composition Root: ensambla settings, engine, middleware de trazabilidad, CORS y routers bajo la fábrica `create_app(settings)`. | Capa API e Infrastructure. | No contiene lógica de negocio ni rutas complejas. |

---

## 3. Modelo de Datos, Relaciones y Restricciones Físicas

### 3.1. Tablas en SQLite (`infrastructure/models.py`)

```python
from sqlmodel import Field, SQLModel, UniqueConstraint

class UsuarioTable(SQLModel, table=True):
    __tablename__ = "usuarios"
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=40)
    password_hash: str = Field(max_length=255)

class ProveedorTable(SQLModel, table=True):
    __tablename__ = "proveedores"
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=120)
    contacto: str = Field(max_length=120)
    telefono: str = Field(max_length=20)
    propietario_id: int = Field(foreign_key="usuarios.id", index=True)

class ProductoTable(SQLModel, table=True):
    __tablename__ = "productos"
    __table_args__ = (
        UniqueConstraint("propietario_id", "codigo", name="uq_producto_propietario_codigo"),
    )
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, max_length=40)
    nombre: str = Field(index=True, max_length=120)
    categoria: str = Field(index=True, max_length=60)
    precio_centavos: int = Field(ge=1)  # Estrictamente mayor que cero
    proveedor_id: int = Field(foreign_key="proveedores.id", index=True)
    propietario_id: int = Field(foreign_key="usuarios.id", index=True)
```

### 3.2. Claves Foráneas y Restricciones Respaldadas por SQLite
1. **Activación Obligatoria de Claves Foráneas:**
   SQLite no valida claves foráneas por defecto. Se activa en cada conexión mediante el listener de SQLAlchemy:
   ```python
   @event.listens_for(engine, "connect")
   def activar_foreign_keys(dbapi_connection, connection_record):
       cursor = dbapi_connection.cursor()
       cursor.execute("PRAGMA foreign_keys=ON")
       cursor.close()
   ```
2. **Restricción de Unicidad Compuesta:**
   La combinación `(propietario_id, codigo)` en `productos` está protegida por un índice único a nivel de motor SQL (`uq_producto_propietario_codigo`), garantizando que la unicidad del código de producto no dependa únicamente de validaciones de software.

---

## 4. Mapeo entre Entidades, Tablas y Esquemas HTTP

Para evitar que cambios en la API impacten la persistencia o que campos de infraestructura se filtren al cliente, se define un mapeo explícito en tres niveles:

```
[Cliente HTTP]
     ▲
     │  (Pydantic Schemas - api/schemas/)
     ▼
[Capa API / Routers]
     ▲
     │  (Entidades de Dominio - domain/)
     ▼
[Capa Application / Use Cases]
     ▲
     │  (Repositorios / UnitOfWork)
     ▼
[Capa Infrastructure / SQLModel Tables - infrastructure/models.py]
     ▲
     │  (SQL / SQLite)
     ▼
[Base de Datos SQLite]
```

### Tabla de Mapeo

| Entidad de Dominio (`domain/`) | Tabla Persistente (`infrastructure/models.py`) | Esquema Entrada HTTP (`api/schemas/`) | Esquema Salida HTTP (`api/schemas/`) |
|---|---|---|---|
| `Usuario(id, username, password_hash)` | `UsuarioTable` (`usuarios`) | `RegistroRequest(username, password)` / `OAuth2PasswordRequestForm` | `UsuarioResponse(id, username)` |
| `Proveedor(id, nombre, contacto, telefono, propietario_id)` | `ProveedorTable` (`proveedores`) | `ProveedorCrear(nombre, contacto, telefono)` / `ProveedorActualizar(...)` | `ProveedorResponse(id, nombre, contacto, telefono)` |
| `Producto(id, codigo, nombre, categoria, precio_centavos, proveedor_id, propietario_id)` | `ProductoTable` (`productos`) | `ProductoCrear(codigo, nombre, categoria, precio_centavos, proveedor_id)` / `ProductoActualizar(...)` | `ProductoResponse(id, codigo, nombre, categoria, precio_centavos, proveedor_id)` |

- **Regla de Ocultamiento:** `propietario_id` y `password_hash` nunca se exponen en los esquemas de respuesta HTTP. El cliente conoce únicamente sus propios datos de negocio.

---

## 5. Gestión de Sesiones y Propietario de Transacciones

- **Problema a evitar:** Commits dispersos en controladores o llamadas repetidas e inconsistentes a `session.commit()`.
- **Patrón Adoptado:**
  1. **Una sesión por petición:** Gestionada por el generador `get_session()` en `infrastructure/database.py`, cerrando la sesión de forma determinista al finalizar la petición HTTP.
  2. **Acceso síncrono a SQLite:** Se utiliza conexión síncrona estándar (`check_same_thread=False`). **No se introduce `async` en la persistencia**; la sobrecarga y complejidad de motores asíncronos para SQLite local no está justificada para este alcance.
  3. **Propietario de la Transacción (Unit of Work / Caso de Uso):**
     - La capa de aplicación delimita la unidad de trabajo (`UnitOfWork`).
     - Las lecturas no abren transacciones de escritura.
     - En operaciones de mutación (`crear`, `actualizar`, `eliminar`), el caso de uso ejecuta las validaciones de dominio y confirma explícitamente (`uow.commit()`). Si se produce cualquier excepción de dominio o error de base de datos, se ejecuta automáticamente `uow.rollback()`.

---

## 6. Manejo del Ciclo de Vida y Estrategia de Esquema

- **Application Factory:** `create_app(settings: Settings | None = None) -> FastAPI`.
- **Lifespan Asíncrono:**
  ```python
  @asynccontextmanager
  async def lifespan(app: FastAPI):
      SQLModel.metadata.create_all(app.state.engine)
      try:
          yield
      finally:
          app.state.engine.dispose()
  ```
- **Documentación sobre `create_all`:**
  `create_all` solo crea tablas que no existan previamente. **No altera ni migra tablas ya existentes ni columnas modificadas.** Si en el futuro se altera el modelo de datos, se debe descartar el archivo `.db` en desarrollo o incorporar una herramienta formal de migraciones (como Alembic).

---

## 7. Configuración, Seguridad y Middleware

1. **Configuración Tipada (`infrastructure/config.py`):**
   - Basada en `pydantic_settings.BaseSettings` con lectura automática de `.env`.
   - Variables requeridas: `DATABASE_URL` (default: `"sqlite:///./la_estrellita.db"`), `JWT_SECRET` (mínimo 32 caracteres, rechaza valores `"REEMPLAZAR..."`), `TOKEN_MINUTES` (default: 30), `CORS_ORIGINS` (default: `["http://localhost:5173"]`).
2. **Autenticación y Criptografía (`infrastructure/security.py`):**
   - **Hashing de contraseñas:** `pwdlib.PasswordHash.recommended()` con algoritmo **Argon2**, siguiendo exactamente la referencia de `observatorio_api`.
   - **Firma de Tokens:** **PyJWT** (`jwt.encode`, `jwt.decode`) con algoritmo `HS256`, emitiendo `exp` calculado en UTC y `sub` conteniendo el `usuario.id` en formato string.
   - **Formato de Login:** El endpoint `POST /api/v1/auth/token` consume `application/x-www-form-urlencoded` con `OAuth2PasswordRequestForm` para compatibilidad completa con Swagger UI y especificación OAuth2.
3. **Middleware de Trazabilidad y Salud:**
   - Middleware ASGI que intercepta cada solicitud, genera un UUIDv4 (`X-Request-ID`), mide el tiempo de respuesta y agrega `X-Process-Time` en segundos a las cabeceras HTTP de salida.
   - `GET /salud`: Endpoint público de liveness en la raíz del servidor, devolviendo `{"estado": "ok"}`.
   - Rutas de negocio agrupadas bajo el prefijo unificado `/api/v1` (`/api/v1/auth`, `/api/v1/proveedores`, `/api/v1/productos`).

---

## 8. Arquitectura y Accesibilidad del Frontend (React + TypeScript)

### 8.1. Gestión de Token y Sesión en Memoria
> ⚠️ **Decisión de Seguridad y Alcance:**
> Para esta versión académica, **el token JWT permanecerá exclusivamente en memoria** (dentro del estado React / Contexto de Autenticación).
> - **Consecuencia directa:** Si el usuario recarga la página (`F5`), el token en memoria se destruye y el usuario deberá volver a iniciar sesión.
> - **Justificación:** Se evita almacenar tokens en `localStorage` (vulnerable a XSS) y se descartan *refresh tokens* o cookies HttpOnly complejas para mantener la arquitectura limpia y proporcional al curso.

### 8.2. Cliente HTTP Centralizado (`frontend/src/shared/api/client.ts`)
- Módulo centralizado basado en `fetch` nativo con tipado TypeScript.
- Inyecta automáticamente la cabecera `Authorization: Bearer <token>` cuando el token en memoria está presente.
- Transforma automáticamente respuestas no exitosas (4xx, 5xx) en objetos de error tipados (`ApiError`) con el detalle provisto por FastAPI.
- Configura automáticamente `Content-Type: application/json` para operaciones de catálogo y `application/x-www-form-urlencoded` para la autenticación.

### 8.3. Accesibilidad Integral (WCAG 2.1 AA / NVDA)
1. **Navegación por Teclado:**
   - Todos los elementos interactivos reciben foco en orden secuencial natural.
   - Los diálogos modales (formularios de alta/edición) capturan el foco (*focus trap*) mientras están abiertos y retornan el foco al elemento disparador al cerrarse (`Escape`).
   - Se incluye un enlace de salto visible al recibir foco: `<a href="#contenido-principal" className="skip-link">Saltar al contenido</a>`.
2. **Formularios y Retroalimentación para Lectores de Pantalla:**
   - Todo campo dispone de `<label htmlFor="id_campo">`.
   - Si ocurre un error de validación, el input se marca con `aria-invalid="true"` y se asocia al mensaje de error mediante `aria-describedby="id_campo-error"`.
   - Los mensajes de éxito o error general se renderizan dentro de contenedores accesibles con `role="status"` o `aria-live="polite"`.
3. **Tablas de Datos:**
   - Tablas con marcado semántico (`<table>`, `<caption>`, `<thead>`, `<tbody>`, `<th scope="col">`).
   - Botones de acción en cada fila con descripción accesible unívoca (ej. `<button aria-label="Eliminar producto Café Grano 500g">`).

---

## 9. Plan de Implementación Dividido en Cambios

El trabajo se divide en 6 paquetes de cambio secuenciales y atómicos:

| Código Cambio | Título del Cambio | Requisitos Cubiertos | Verificación Esperada |
|---|---|---|---|
| **01-base-tecnica** | Andamiaje Modular, Configuración, SQLite y Middleware | `REQ-SYS-01`, `REQ-SYS-02`, `REQ-SYS-03`, `S1`, `S3`, `S6`, `S7`, `T09`, `T10`, `T11`, `T12` | Endpoint `/salud` responde 200; middleware inyecta `X-Request-ID` y `X-Process-Time`; SQLite inicializa tablas con `PRAGMA foreign_keys=ON`; settings valida `.env`. |
| **02-autenticacion** | Seguridad, Hashing Argon2, JWT y Rutas `/api/v1/auth` | `REQ-AUTH-01` a `04`, `S13`, `S16`, `S24`, `T12`, `T13` | Registro `POST /api/v1/auth/registro` (201); login con form-urlencoded `POST /api/v1/auth/token` (200); perfil `GET /api/v1/auth/yo` (200); rechazo con token inválido/vencido (401). |
| **03-proveedores** | Dominio, Repositorio y CRUD de Proveedores con Propiedad | `REQ-PROV-01` a `06`, `S14`, `S15`, `S17`, `S19`, `S22`, `S23`, `T01`, `T02`, `T03`, `T04`, `T05`, `T07`, `T14` | Tests CRUD de proveedores; verificación de que usuario B recibe 404 al consultar proveedor de usuario A; validación anti-null en PATCH. |
| **04-productos** | Dominio, Repositorio y CRUD de Productos con Validación Cruzada | `REQ-PROD-01` a `06`, `S14`, `S15`, `S17`, `S18`, `S20`, `S21`, `S22`, `T06`, `T08` | Creación de producto vinculando proveedor propio (201); rechazo al vincular proveedor ajeno (404); rechazo de código duplicado para el mismo usuario (409); rechazo 409 al borrar proveedor con productos. |
| **05-consultas-trazabilidad** | Búsqueda, Filtros Combinados, Paginación y Frontend Base | `REQ-PROV-02`, `REQ-PROD-02`, `REQ-A11Y-01` a `05`, `S2`, `S4`, `S5`, `T15` | Filtros por texto `q`, categoría y paginación `offset`/`limite`; cliente HTTP en React con token en memoria; navegación accesible por teclado en tablas y modales. |
| **06-verificacion-entrega** | Suite Integral de Pruebas Pytest, Verificación NVDA y Docs | `S8`, `S9`, `S10`, `S11`, `S12`, `T13`, `T15`, Criterios de Finalización | Cobertura total de pruebas en base SQLite temporal (`tmp_path`); verificación con NVDA en Windows; documentación de ejecución y entrega completa. |

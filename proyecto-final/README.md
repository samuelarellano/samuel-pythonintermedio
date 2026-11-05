# La Estrellita — Catálogo de Proveedores y Productos

Sistema web para gestión de catálogos comerciales con arquitectura limpia en **monolito modular**.
Construido con backend **Python (FastAPI, SQLModel, Pydantic v2, SQLite)** y frontend **React (TypeScript, Vite)**, diseñado con accesibilidad nativa (**WCAG 2.1 AA**) para teclado y lector de pantalla **NVDA**.

Proyecto final del curso **Python Intermedio**, impartido por el profesor **Emmanuel Pulido**.

---

## 1. Arquitectura del Monolito Modular

El sistema está estructurado respetando la separación estricta de responsabilidades por capas:

```
proyecto-final/
├── backend/
│   ├── app/
│   │   ├── domain/               # Entidades puras y reglas de negocio (sin dependencias web ni ORM)
│   │   │   ├── usuario.py        # Entidad Usuario
│   │   │   ├── proveedor.py      # Entidad Proveedor
│   │   │   ├── producto.py       # Entidad Producto
│   │   │   └── exceptions.py     # Excepciones de negocio (ProveedorNoEncontrado, etc.)
│   │   ├── application/          # Casos de uso y contratos de puertos (Protocols)
│   │   │   ├── interfaces/       # Contratos IProveedorRepository, IProductoRepository
│   │   │   └── use_cases/        # ProveedorUseCases, ProductoUseCases
│   │   ├── infrastructure/       # SQLite, SQLModel, settings y seguridad concreta
│   │   │   ├── config.py         # Settings tipada con pydantic-settings
│   │   │   ├── database.py       # Engine SQLite síncrono, PRAGMA foreign_keys=ON y get_session
│   │   │   ├── models.py         # Tablas persistentes (UsuarioTable, ProveedorTable, ProductoTable)
│   │   │   ├── security.py       # Argon2 (pwdlib) con DUMMY_HASH y PyJWT (HS256)
│   │   │   ├── middleware.py     # Observabilidad ASGI (X-Request-ID, X-Process-Time)
│   │   │   └── repositories/     # Adaptadores concretos SqlProveedorRepository, SqlProductoRepository
│   │   ├── api/                  # Capa HTTP (FastAPI, esquemas Pydantic v2 y routers)
│   │   │   ├── dependencies.py   # Inyección de dependencias (SessionDep, UsuarioDep)
│   │   │   ├── schemas/          # Contratos HTTP (auth_schemas, proveedor_schemas, producto_schemas)
│   │   │   └── routers/          # Endpoints (/api/v1/auth, /api/v1/proveedores, /api/v1/productos)
│   │   └── main.py               # Composition Root: create_app(settings), lifespan y CORS
│   └── tests/                    # 30 pruebas unitarias e integrales con pytest y tmp_path
└── frontend/
    └── src/
        ├── features/             # Módulos funcionales: auth, proveedores, productos
        └── shared/               # Cliente HTTP tipado, formateador de moneda MXN, componentes accesibles
```

---

## 2. Decisiones Académicas y Limitaciones Conocidas

1. **Aislamiento Multi-inquilino de Catálogos:**
   - *Decisión:* Cada usuario autenticado gestiona su propio catálogo privado e independiente de proveedores y productos.
   - *Nota de gobernanza:* Esta es una decisión de diseño de proyecto para demostrar el dominio del patrón de seguridad de `observatorio_api`, y **no constituye un requisito confirmado por el profesor Emmanuel Pulido**.
2. **Gestión de Sesión en Memoria (React):**
   - El token JWT se conserva exclusivamente en memoria en el contexto de React (`AuthContext`).
   - *Consecuencia:* Recargar la página (`F5`) destruye el token en memoria y requiere iniciar sesión nuevamente.
   - *Motivo:* Evitar vulnerabilidades de almacenamiento en `localStorage` (XSS) y prescindir de la complejidad de *refresh tokens* innecesarios para esta entrega académica.
3. **Manejo Monetario sin Coma Flotante:**
   - Todo precio se almacena en backend y base de datos como un entero en centavos (`precio_centavos: int > 0`).
   - El frontend permite ingresar pesos con decimales, pero realiza una conversión determinista descomponiendo parte entera y decimal (`pesosACentavos`) antes de enviar el entero al servidor.
4. **Estrategia de Creación de Esquema con `create_all`:**
   - En el `lifespan` de `main.py` se ejecuta `SQLModel.metadata.create_all(engine)`.
   - *Limitación:* `create_all` solo crea tablas ausentes; **no migra tablas existentes ni nuevas columnas**. Cambios posteriores requieren descartar el archivo `.db` en desarrollo o incorporar Alembic.

---

## 3. Preparación y Ejecución en PowerShell

### Requisitos Previos
- **Python 3.10 o superior** (verificado con Python 3.14 en Windows).
- **Node.js v18+ y npm** (verificado con Node v22.15.0).
- No requiere activar manualmente entornos virtuales; los comandos usan directamente el ejecutable del `.venv`.

---

### Paso 1: Configurar y Ejecutar el Backend (FastAPI)

Desde la carpeta raíz del proyecto (`proyecto-final`), abre una terminal PowerShell:

```powershell
# 1. Crear el entorno virtual en backend (si no existe)
cd backend
python -m venv .venv

# 2. Instalar dependencias exactas y de desarrollo
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

# 3. Configurar archivo de variables de entorno (.env)
Copy-Item env.example .env

# 4. Generar un secreto JWT seguro de 32 bytes (64 caracteres hex)
$secreto = .\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
(Get-Content .env) -replace "REEMPLAZAR_CON_TOKEN_HEX_DE_32_BYTES_MINIMO_0123456789abcdef", $secreto | Set-Content .env

# 5. Iniciar el servidor Uvicorn con recarga automática
.\.venv\Scripts\python.exe -m uvicorn app.main:create_app --factory --reload --port 8000
```

- Documentación interactiva Swagger UI: **http://127.0.0.1:8000/docs**
- Documentación ReDoc: **http://127.0.0.1:8000/redoc**
- Endpoint de salud y trazabilidad: **http://127.0.0.1:8000/salud**

---

### Paso 2: Ejecutar las Pruebas del Backend (Pytest)

En cualquier momento podés ejecutar la suite completa de pruebas automatizadas:

```powershell
# Desde la carpeta backend:
.\.venv\Scripts\python.exe -m pytest tests -v
```

Todas las pruebas se ejecutan en **bases de datos SQLite efímeras y aisladas** (`tmp_path`), garantizando que la base de desarrollo `la_estrellita.db` jamás se altere.

---

### Paso 3: Configurar y Ejecutar el Frontend (React + Vite)

Abre una segunda terminal PowerShell:

```powershell
cd frontend

# 1. Instalar dependencias de Node
npm install

# 2. Configurar variable de entorno para URL de la API
Copy-Item env.example .env

# 3. Comprobar tipado estricto de TypeScript
npm run lint

# 4. Iniciar el servidor de desarrollo Vite
npm run dev
```

- Interfaz accesible disponible en: **http://localhost:5173**

---

## 4. Matriz de Trazabilidad: Temas del Curso → Implementación → Pruebas

| Código | Tema del Curso / Referencia | Origen | Implementación en La Estrellita | Verificación Ejecutable |
|---|---|---|---|---|
| **T01** | Routing HTTP, verbos REST y códigos de estado (200, 201, 204, 404, 409, 422) | `biblioteca_aula` | Routers `/auth`, `/proveedores` y `/productos` en `app/api/routers/` | Tests en `test_proveedores.py` y `test_productos.py` validando códigos exactos. |
| **T02** | Validación estricta con Pydantic v2 (`Path`, `Query`, `Field`, `extra="forbid"`) | `biblioteca_aula` | Esquemas en `app/api/schemas/` con validación de cadenas y longitudes | `test_validaciones_contrato_422`: inyección de campos extra o IDs negativos devuelve 422. |
| **T03** | Distinción de campos omitidos vs. `null` explícito en `PATCH` | `observatorio_api` | Validador `@field_validator(..., no_null)` en schemas de actualización | Tests enviando `{"nombre": null}` confirman rechazo con 422. |
| **T04** | Modularización con `APIRouter` y etiquetas de OpenAPI | `cafeteria_campus` | Routers modulares incluidos bajo `/api/v1` en `main.py` | Agrupación limpia observable en Swagger UI (`/docs`). |
| **T05** | Inyección de dependencias con `Depends` | `cafeteria_campus` | `SessionDep` y `UsuarioDep` inyectados en endpoints | Fixtures en `conftest.py` y pruebas de endpoints protegidos. |
| **T06** | Precios en centavos enteros (`precio_centavos: int > 0`) | `cafeteria_campus` | Invariante de dominio en `Producto` y formateador visual en frontend | `test_validaciones_precio_centavos_y_anti_null`: rechaza floats y ceros. |
| **T07** | Persistencia relacional con SQLModel y SQLite | `observatorio_api` | Tablas `UsuarioTable`, `ProveedorTable`, `ProductoTable` | `test_persistencia_sobrevive_reinicio`: datos sobreviven al reiniciar app. |
| **T08** | Claves foráneas activas en SQLite (`PRAGMA foreign_keys=ON`) | `observatorio_api` | Listener SQLAlchemy `@event.listens_for(engine, "connect")` | `test_aislamiento_base_de_datos_temporal` verifica `PRAGMA foreign_keys = 1`. |
| **T09** | Restricción de unicidad compuesta en motor SQL | Nuevo requisito | `UniqueConstraint("propietario_id", "codigo")` en `ProductoTable` | `test_unicidad_codigo_por_usuario`: mismo usuario da 409; usuarios distintos da 201. |
| **T10** | Application Factory (`create_app`) y ciclo de vida asíncrono (`lifespan`) | `observatorio_api` | Función `create_app` con `lifespan` en `app/main.py` | Arranca con bases temporales aisladas en cada test sin estado global. |
| **T11** | Configuración tipada con `pydantic-settings` y rechazo de secretos de ejemplo | `observatorio_api` | `Settings` en `app/infrastructure/config.py` | `test_settings_rechaza_marcador_inseguro`: arroja `ValidationError`. |
| **T12** | Middleware de trazabilidad (`X-Request-ID`, `X-Process-Time`) | `observatorio_api` | Middleware ASGI en `app/infrastructure/middleware.py` | `test_middleware_headers_en_exito_y_errores`: presente en 200, 401, 404, 422. |
| **T13** | Seguridad OAuth2, tokens JWT con PyJWT y hash Argon2 con pwdlib | `observatorio_api` | `security.py` con `DUMMY_HASH`, login form-urlencoded y claims `sub`, `iat`, `exp` | `test_auth.py`: 10 pruebas cubriendologin, contraseñas malas, tokens vencidos. |
| **T14** | Aislamiento y comprobación estricta de propiedad en todas las operaciones | `observatorio_api` | `propietario_id == usuario.id` en use cases y queries | `test_aislamiento_estricto_entre_dos_usuarios`: Usuario B recibe 404 ante datos de A. |
| **T15** | Integridad de negocio: Impedir eliminación de proveedor con productos | Regla de negocio | Verificación previa en `ProveedorUseCases.eliminar` | `test_impedir_eliminacion_proveedor_con_productos_409`: responde 409 Conflict. |
| **T16** | Búsqueda literal con autoescape para comodines SQL (% y _) | `observatorio_api` | `contains(q, autoescape=True)` en repositorios SQL | `test_busqueda_literal_con_comodines_sql_autoescape`: búsqueda literal verificada. |
| **T17** | Interfaz web accesible (WCAG 2.1 AA) para teclado y lector NVDA | Requisito final | React + TypeScript con HTML semántico, skip link, regiones vivas y modales | `npm run lint` y `npm run build` limpios; protocolo manual de prueba NVDA. |

---

## 5. Pruebas Manuales con `peticiones.http`

El archivo `peticiones.http` en la raíz permite ejecutar todo el flujo desde clientes REST sin necesidad de navegador:
1. `GET /salud`: Comprobación de liveness.
2. `POST /api/v1/auth/registro`: Registro de dos comerciantes (`comerciante_demo_a` y `comerciante_demo_b`).
3. `POST /api/v1/auth/token`: Inicio de sesión mediante formulario urlencoded obteniendo los tokens Bearer.
4. CRUD de Proveedores y Productos con usuario A.
5. Verificación de que usuario B recibe `404 Not Found` al intentar consultar o modificar recursos de A.
6. Verificación de que intentar eliminar un proveedor con productos devuelve `409 Conflict`.
7. Casos inválidos (precios en cero, inyección de `propietario_id` con 422, `null` explícito en PATCH con 422).

---

## 6. Protocolo de Verificación Accesible con Lector de Pantalla NVDA

> ⚠️ **Transparencia ética:** Las comprobaciones en el entorno de desarrollo se ejecutaron mediante compilación estricta de TypeScript, inspección semántica del árbol DOM y navegación por teclado. **No se emitió una afirmación falsa de haber ejecutado el software NVDA en modo autónomo**. A continuación se detalla el recorrido exacto para que **Samuel** lo ejecute y compruebe en Windows:

### Recorrido Paso a Paso con NVDA
1. **Arranque y foco inicial:**
   - Inicia **NVDA** (`Ctrl + Alt + N`).
   - Abre el navegador en `http://localhost:5173`.
   - Presiona `Tab`: el primer elemento enfocado debe ser el **Skip Link** *"Saltar al contenido principal"*. Pulsa `Enter` para comprobar que el foco se traslada al contenedor `<main>`.
2. **Registro e Inicio de Sesión:**
   - Navega con `Tab` al botón *"Registrarse"* y pulsa `Enter`.
   - Completa el formulario de registro: verifica que NVDA verbaliza cada `<label>` asociado (*"Nombre de usuario: campo de edición"*, *"Contraseña: campo de edición protegido"*).
   - Intenta enviar con un usuario de 2 caracteres: NVDA debe leer de inmediato el mensaje de error verbalizado mediante el `role="alert"` (*"El nombre de usuario debe tener entre 3 y 40 caracteres"*).
   - Completa un usuario válido (ej. `samuel_demo`) y contraseña (`ContraseniaSegura2026!`). Pulsa `Enter`: el sistema inicia sesión automáticamente y anuncia el estado en la región viva.
3. **Catálogo de Proveedores:**
   - Con la sesión iniciada, navega con `Tab` hasta *"Proveedores"* y pulsa `Enter`.
   - Si no hay proveedores, NVDA leerá el aviso de catálogo vacío.
   - Pulsa en *"+ Nuevo Proveedor"*: se abrirá el modal accesible.
   - **Comprobación de foco:** El cursor debe ubicarse automáticamente en el campo *"Razón Social / Nombre"*.
   - Pulsa `Escape`: el modal debe cerrarse y el foco debe **regresar exactamente al botón "+ Nuevo Proveedor"**.
   - Abre el modal nuevamente, guarda un proveedor (ej. "Cafés de Chiapas", "Elena Ruiz", "555-888-9999"). NVDA anunciará en la región viva: *"Proveedor Cafés de Chiapas creado exitosamente"*.
   - Recorre la tabla con teclas de flecha de tabla de NVDA (`Ctrl + Alt + Flechas`): comprueba que lee los encabezados `<th>` (*Razón Social*, *Contacto*, *Teléfono*, *Acciones*).
   - En la columna de acciones, presiona `Tab`: los botones deben verbalizarse como *"Editar proveedor Cafés de Chiapas"* y *"Eliminar proveedor Cafés de Chiapas"*.
4. **Catálogo de Productos y Selector:**
   - Navega a *"Productos"*.
   - Pulsa *"+ Nuevo Producto"*.
   - Comprueba que el selector `<select>` contiene a "Cafés de Chiapas" como opción accesible.
   - Ingresa un precio con decimales (ej. `120.50`). Al guardar, se convertirá a centavos (`12050`) y la tabla lo anunciará como `"$120.50 MXN"`.
5. **Prueba de Eliminación y Regla de Integridad:**
   - Regresa a *"Proveedores"*.
   - Pulsa en *"Eliminar proveedor Cafés de Chiapas"*.
   - Se abrirá el diálogo modal `alertdialog`: el foco se colocará de manera segura en el botón *"Cancelar"*.
   - Pulsa en *"Eliminar"*: la API rechazará la acción y NVDA leerá la alerta: *"No se puede eliminar el proveedor porque tiene productos asociados"*.

---

## 7. Guion Breve para Demostración al Profesor Emmanuel Pulido (5 Minutos)

Para presentar y defender el proyecto ante el docente:

1. **Introducción y Arquitectura (1 minuto):**
   - *"Profesor, el proyecto La Estrellita es un catálogo comercial de proveedores y productos desarrollado con un monolito modular limpio. Separamos Dominio, Aplicación, Infraestructura y API sin sobreingeniería: cero microservicios, cero colas de mensajes y sin repositorios genéricos redundantes."*
2. **Trazabilidad de Conceptos del Curso (1 minuto):**
   - *"Retomamos los fundamentos de biblioteca_aula (validación con Pydantic v2, errores 422, parámetros Path y Query); de cafeteria_campus tomamos los APIRouters modulares, inyección Depends y el manejo monetario seguro en centavos enteros; y de observatorio_api incorporamos el Application Factory con lifespan, SQLite con PRAGMA foreign_keys forzoso, pydantic-settings, middleware de trazabilidad y seguridad OAuth2 con JWT y Argon2."*
3. **Aislamiento Multi-inquilino y Restricciones (1.5 minutos):**
   - *"Demostramos el catálogo privado: mostramos dos cuentas (`usuario_a` y `usuario_b`). Al consultar los proveedores de A con el token de B, el sistema responde `404 Not Found` para proteger la privacidad. Mostramos también la restricción de base de datos `UniqueConstraint('propietario_id', 'codigo')`, permitiendo que ambos usuarios tengan su propio producto 'P-01' sin conflicto."*
   - *"Mostramos la regla de negocio de integridad: intentar borrar un proveedor con productos devuelve `409 Conflict`."*
4. **Demostración de Accesibilidad en React (1.5 minutos):**
   - *"En el frontend, el token JWT vive estrictamente en memoria para máxima seguridad contra XSS. La interfaz cumple WCAG 2.1 AA: demostramos la navegación 100% por teclado (`Tab`, Skip Link, atrapamiento y retorno de foco en modales con `Escape`) y las regiones vivas (`aria-live`) preparadas para lectores de pantalla como NVDA."*
5. **Cierre y Pruebas:**
   - Ejecutar `pytest tests` en la terminal para mostrar las **30 pruebas pasando al 100%** en base SQLite temporal aislada sin tocar la base de desarrollo.

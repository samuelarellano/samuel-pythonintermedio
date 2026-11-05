# Especificación Funcional y Técnica SDD: La Estrellita
`openspec/specs/catalogo-la-estrellita.md`
Versión: 1.1.0 | Estado: Aprobada para desarrollo | Metodología: SDD (Gentle Shell / el Gentleman)

---

## 1. Decisión de Arquitectura y Alcance Académico

> **Nota de Gobernanza y Alcance:**
> Se establece que **cada usuario autenticado dispondrá de su propio catálogo privado e independiente de proveedores y productos**.
> **Registro explícito:** Esta es una **decisión de diseño del proyecto** inspirada en el patrón de propiedad de `observatorio_api` y **no constituye un requisito confirmado por el profesor Emmanuel Pulido**. Permite evaluar las competencias de seguridad (OAuth2 + JWT + Argon2), aislamiento multi-inquilino a nivel de fila y control de acceso estricto.

### 1.1. Exclusiones Explícitas del Sistema
Para mantener una arquitectura limpia y proporcional, quedan **fuera de alcance**:
- Módulos de ventas, facturación o cobros.
- Carritos o pedidos (se mantienen en `cafeteria_campus` como referencia).
- Control de inventario avanzado (lotes, fechas de caducidad, movimientos de stock, alertas de reorden).
- Roles administrativos jerárquicos (RBAC complejo, superusuarios, moderación).
- Microservicios, colas de mensajes, Event Sourcing y repositorios genéricos.

---

## 2. Modelos de Dominio Mínimos y Contratos de Datos

Se prioriza el minimalismo: se eliminan datos fiscales complejos (RFC), direcciones extensas e inventario innecesario.

### 2.1. Tablas Persistentes (`models.py`)

```python
from sqlmodel import Field, SQLModel, UniqueConstraint

class Usuario(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True, max_length=40)
    password_hash: str = Field(max_length=255)

class Proveedor(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(index=True, max_length=120)
    contacto: str = Field(max_length=120)
    telefono: str = Field(max_length=20)
    propietario_id: int = Field(foreign_key="usuario.id", index=True)

class Producto(SQLModel, table=True):
    __table_args__ = (
        UniqueConstraint("propietario_id", "codigo", name="uq_producto_propietario_codigo"),
    )
    id: int | None = Field(default=None, primary_key=True)
    codigo: str = Field(index=True, max_length=40)
    nombre: str = Field(index=True, max_length=120)
    categoria: str = Field(index=True, max_length=60)
    precio_centavos: int = Field(gt=0)
    proveedor_id: int = Field(foreign_key="proveedor.id", index=True)
    propietario_id: int = Field(foreign_key="usuario.id", index=True)
```

### 2.2. Restricciones y Reglas de Dominio
1. **Asignación de Autoridad:** El servidor es la única entidad que asigna `id`, `propietario_id` y marcas de auditoría. Cualquier intento del cliente de enviar `id` o `propietario_id` en el cuerpo JSON es rechazado con `422 Unprocessable Entity` (`extra="forbid"`).
2. **Normalización de Cadenas:** Todos los campos de texto eliminan espacios en blanco en extremos (`str_strip_whitespace=True`) y no pueden quedar vacíos (`min_length=1`).
3. **Unicidad de Código:** El campo `codigo` es único **dentro del catálogo del usuario propietario**. Dos usuarios distintos pueden tener un producto con código `"PROD-01"`, pero un mismo usuario no puede repetirlo (restringido en base de datos con `UniqueConstraint("propietario_id", "codigo")`).
4. **Validación de Relación Cruzada:** Un producto **solo puede asociarse a un proveedor que pertenezca al mismo usuario autenticado**. Si se intenta vincular un proveedor inexistente o perteneciente a otro usuario, el servidor responde `404 Not Found`.
5. **Protección de Eliminación (Integridad de Negocio):** No se permite eliminar un proveedor si tiene productos asociados. El servidor verifica la existencia de productos dependientes y responde `409 Conflict`.
6. **Manejo Monetario:** `precio_centavos` es un entero estrictamente mayor a cero (`gt=0`). Prohibido el uso de tipos flotantes en backend y almacenamiento.
7. **Semántica de Actualización (`PATCH`):**
   - Si un campo se omite en el payload, conserva su valor actual.
   - Si un campo se envía explícitamente con valor `null`, se rechaza con `422 Unprocessable Entity` mediante validador (`no_null`).
8. **Seguridad en Esquemas de Salida:** Los contratos de respuesta pública (`UsuarioPublico`, `ProveedorPublico`, `ProductoPublico`) excluyen terminantemente hashes de contraseña (`password_hash`), tokens y secretos internos.

---

## 3. Requisitos Funcionales con Identificadores Estables

### Módulo: Autenticación y Perfil (AUTH)
- **REQ-AUTH-01 (Registro):** El sistema debe permitir el registro público de nuevos usuarios mediante nombre de usuario (alfanumérico en minúsculas y guion bajo, 3 a 40 caracteres) y contraseña (mínimo 12 caracteres).
- **REQ-AUTH-02 (Login y Token):** El sistema debe autenticar usuarios mediante `application/x-www-form-urlencoded` compatible con OAuth2 Password Flow, retornando un token JWT tipo Bearer con vencimiento y cabecera `Cache-Control: no-store`.
- **REQ-AUTH-03 (Perfil Actual):** El endpoint `GET /auth/yo` debe devolver la información pública del usuario autenticado a partir del token Bearer.
- **REQ-AUTH-04 (Aislamiento de Sesión):** Cualquier petición a rutas protegidas sin token, con token vencido, firma alterada o usuario inexistente debe ser rechazada con `401 Unauthorized` y cabecera `WWW-Authenticate: Bearer`.

### Módulo: Proveedores (PROV)
- **REQ-PROV-01 (Crear Proveedor):** Un usuario autenticado puede crear un proveedor enviando `nombre`, `contacto` y `telefono`. El servidor asocia el proveedor al `usuario.id` del token y responde `201 Created`.
- **REQ-PROV-02 (Listar Proveedores Propios):** `GET /proveedores` debe retornar únicamente los proveedores pertenecientes al usuario autenticado, admitiendo filtro de texto `q` (búsqueda parcial insensible a mayúsculas sobre `nombre`) y paginación (`offset >= 0`, `limite` entre 1 y 100).
- **REQ-PROV-03 (Consultar Proveedor):** `GET /proveedores/{id}` retorna el detalle del proveedor si pertenece al usuario.
- **REQ-PROV-04 (Actualizar Proveedor):** `PATCH /proveedores/{id}` permite actualizar parcialmente `nombre`, `contacto` o `telefono` del proveedor propio.
- **REQ-PROV-05 (Eliminar Proveedor Seguro):** `DELETE /proveedores/{id}` elimina el proveedor propio solo si no tiene productos asociados, respondiendo `204 No Content`. Si tiene productos vinculados, rechaza con `409 Conflict`.
- **REQ-PROV-06 (Aislamiento de Propiedad):** Si el proveedor solicitado por `{id}` no existe o pertenece a otro usuario, el sistema responde `404 Not Found` en todas las operaciones (`GET`, `PATCH`, `DELETE`).

### Módulo: Productos (PROD)
- **REQ-PROD-01 (Crear Producto Vinculado):** Un usuario autenticado puede registrar un producto enviando `codigo`, `nombre`, `categoria`, `precio_centavos` y `proveedor_id`. El servidor valida que el proveedor exista y pertenezca al usuario; de lo contrario, responde `404 Not Found`. Si el código ya existe para ese usuario, responde `409 Conflict`.
- **REQ-PROD-02 (Listar Productos Propios):** `GET /productos` lista los productos del usuario autenticado, permitiendo filtros combinables: `q` (sobre `nombre` o `codigo`), `categoria` exacta, `proveedor_id` específico y paginación (`offset`, `limite`).
- **REQ-PROD-03 (Consultar Producto):** `GET /productos/{id}` retorna el producto si pertenece al usuario.
- **REQ-PROD-04 (Actualizar Producto):** `PATCH /productos/{id}` actualiza campos permitidos. Si se intenta cambiar `proveedor_id`, se valida que el nuevo proveedor pertenezca al usuario (o `404`). Si se cambia `codigo`, se valida unicidad en el catálogo del usuario (o `409`).
- **REQ-PROD-05 (Eliminar Producto):** `DELETE /productos/{id}` elimina el producto propio respondiendo `204 No Content`.
- **REQ-PROD-06 (Aislamiento de Propiedad):** Cualquier operación sobre un producto de otro usuario responde `404 Not Found`.

### Módulo: Observabilidad y Plataforma (SYS)
- **REQ-SYS-01 (Trazabilidad HTTP):** Todo request procesado por la API debe recibir una cabecera `X-Request-ID` con un UUIDv4 único y `X-Process-Time` con la duración en segundos, reflejadas tanto en respuestas exitosas como en errores controlados.
- **REQ-SYS-02 (Salud del Proceso):** `GET /salud` responde `{"estado": "ok"}` sin requerir autenticación.
- **REQ-SYS-03 (CORS Restringido):** La API solo acepta peticiones cruzadas desde orígenes declarados en configuración (por defecto `http://localhost:5173`).

---

## 4. Escenarios BDD (Dado / Cuando / Entonces)

### Escenario 1: Creación de Proveedor y Aislamiento de Catálogo
```gherkin
Característica: Aislamiento estricto de catálogo entre usuarios

  Escenario: Un usuario no puede ver ni acceder a los proveedores creados por otro
    Dado que existen dos usuarios registrados: "comerciante_a" y "comerciante_b"
    Y "comerciante_a" ha iniciado sesión y tiene un token válido
    Cuando "comerciante_a" envía un POST a "/proveedores" con:
      | nombre    | Distribuidora Central |
      | contacto  | Juan Pérez            |
      | telefono  | 555-123-4567          |
    Entonces el servidor responde 201 Created
    Y el cuerpo incluye un "id" asignado y los datos enviados
    Y no se incluye "password_hash" ni "propietario_id" en la respuesta
    Cuando "comerciante_b" inicia sesión con su propio token
    Y envía un GET a "/proveedores"
    Entonces el servidor responde 200 OK con una lista vacía "[]"
    Cuando "comerciante_b" envía un GET a "/proveedores/{id_de_comerciante_a}"
    Entonces el servidor responde 404 Not Found con mensaje "Proveedor no encontrado"
```

### Escenario 2: Creación de Producto y Validación de Proveedor Ajeno
```gherkin
Característica: Integridad referencial de propiedad en productos

  Escenario: Intentar asociar un producto a un proveedor de otro usuario es rechazado
    Dado que "comerciante_a" tiene un proveedor registrado con id=10
    Y "comerciante_b" tiene una sesión activa
    Cuando "comerciante_b" envía un POST a "/productos" con:
      | codigo          | PROD-999             |
      | nombre          | Harina de Trigo 1kg  |
      | categoria       | Abarrotes            |
      | precio_centavos | 2500                 |
      | proveedor_id    | 10                   |
    Entonces el servidor responde 404 Not Found
    Y el mensaje de detalle indica "Proveedor no encontrado"
    Y ningún producto es persistido en la base de datos
```

### Escenario 3: Unicidad de Código por Catálogo de Usuario
```gherkin
Característica: Unicidad del código de producto por usuario

  Escenario: El mismo usuario no puede repetir código, pero usuarios distintos sí
    Dado que "comerciante_a" tiene registrado el producto con codigo="CAFE-01"
    Cuando "comerciante_a" intenta registrar otro producto con codigo="CAFE-01"
    Entonces el servidor responde 409 Conflict con mensaje "Código de producto ya registrado"
    Cuando "comerciante_b" registra un producto con codigo="CAFE-01" bajo su propio proveedor
    Entonces el servidor responde 201 Created con éxito
```

### Escenario 4: Protección de Integridad al Eliminar Proveedor con Productos
```gherkin
Característica: Protección de borrado de proveedores vinculados

  Escenario: Rechazo de eliminación de proveedor con productos asociados
    Dado que "comerciante_a" tiene un proveedor con id=5
    Y tiene al menos un producto asociado a dicho proveedor
    Cuando "comerciante_a" envía un DELETE a "/proveedores/5"
    Entonces el servidor responde 409 Conflict
    Y el cuerpo indica "No se puede eliminar el proveedor porque tiene productos asociados"
    Y el proveedor permanece registrado y consultable
```

### Escenario 5: Actualización Parcial Rigurosa (`PATCH`)
```gherkin
Característica: Semántica de PATCH y rechazo de null

  Escenario: Enviar null en un campo opcional es rechazado con 422
    Dado que el usuario autenticado tiene un producto id=1
    Cuando envía un PATCH a "/productos/1" con JSON '{"nombre": null}'
    Entonces el servidor responde 422 Unprocessable Entity
    Y el error detalla que debe omitirse el campo si no desea modificarse
    Cuando envía un PATCH a "/productos/1" con JSON '{"precio_centavos": 3200}'
    Entonces el servidor responde 200 OK con el nuevo precio y conserva el nombre intacto
```

---

## 5. Matriz de Códigos HTTP y Contratos de Error

### 5.1. Códigos Utilizados en la API
| Código | Significado | Escenario de Uso |
|---|---|---|
| `200 OK` | Operación exitosa con cuerpo | Listar, obtener detalle, actualización `PATCH` exitosa, perfil `/auth/yo`, token. |
| `201 Created` | Creación exitosa | Alta de usuario (`/auth/registro`), alta de proveedor, alta de producto. |
| `204 No Content` | Eliminación exitosa sin cuerpo | `DELETE` de producto o proveedor sin dependencias. |
| `400 Bad Request` | Petición semánticamente inválida | Errores de sintaxis o violaciones lógicas previas a DB. |
| `401 Unauthorized` | Falla de autenticación | Token faltante, expirado, inválido o credenciales erróneas en login. Incluye `WWW-Authenticate: Bearer`. |
| `404 Not Found` | Recurso no encontrado o ajeno | ID no existe en la base de datos o pertenece a otro usuario (no revela existencia). |
| `409 Conflict` | Conflicto de unicidad o integridad | Username ya ocupado, código de producto duplicado en el catálogo propio, eliminación de proveedor con productos. |
| `422 Unprocessable Entity` | Contrato o tipos inválidos | Campos faltantes requeridos, campos inesperados (`extra="forbid"`), cadenas vacías tras trim, `precio_centavos <= 0`, o envío de `null` en PATCH. |

### 5.2. Formato Canónico de Respuestas de Error
```json
{
  "detail": "Descripción comprensible del error para el cliente"
}
```
Para errores de validación de FastAPI/Pydantic (422), se mantiene el estándar nativo con localización:
```json
{
  "detail": [
    {
      "loc": ["body", "precio_centavos"],
      "msg": "Input should be greater than 0",
      "type": "greater_than"
    }
  ]
}
```

---

## 6. Requisitos de Accesibilidad del Frontend (WCAG 2.1 AA / NVDA)

- **REQ-A11Y-01 (Navegabilidad 100% por Teclado):** Toda la interfaz debe ser completamente utilizable sin mouse:
  - Navegación secuencial lógica (`Tab` / `Shift+Tab`).
  - Activación con `Enter` y `Espacio` en botones y toggles.
  - Cierre de modales/diálogos con tecla `Escape`.
  - Enlaces de salto directo al contenido principal (*Skip to Main Content*).
- **REQ-A11Y-02 (Indicadores de Foco Visibles):** Cada elemento interactivo en foco debe presentar un indicador de alto contraste (mínimo ratio 3:1 contra el fondo adyacente). Prohibido `outline: none` sin sustituto visual.
- **REQ-A11Y-03 (Semántica para NVDA y Lectores de Pantalla):**
  - Uso estricto de etiquetas semánticas (`<header>`, `<nav>`, `<main>`, `<footer>`, `<section>`).
  - Formularios: Cada `<input>`, `<select>` y `<textarea>` tiene un `<label htmlFor="...">` unívoco.
  - Mensajes de error en inputs asociados con `aria-describedby="id-error"` y `aria-invalid="true"`.
- **REQ-A11Y-04 (Regiones Vivas y Feedback Dinámico):**
  - Las alertas de error, mensajes de éxito tras guardar y estados de carga deben comunicarse a NVDA usando `role="status"` o `aria-live="polite"` / `aria-live="assertive"`.
- **REQ-A11Y-05 (Tablas de Datos Accesibles):**
  - Las listas de proveedores y productos deben implementarse como tablas HTML (`<table>`) con `<caption>`, `<thead>`, `<tbody>` y encabezados `<th>` con atributo `scope="col"`.
  - Los botones de acción en filas deben tener nombres accesibles inequívocos (ej. `<button aria-label="Editar proveedor Frutas del Valle">`).

---

## 7. Criterios de Aceptación y Finalización (Definition of Done)

Para considerar concluida la entrega en fases posteriores:
1. **Especificación Verificada:** Todos los requisitos (`REQ-AUTH`, `REQ-PROV`, `REQ-PROD`, `REQ-SYS`, `REQ-A11Y`) cuentan con pruebas automáticas o verificaciones manuales asociadas en la matriz de trazabilidad.
2. **Backend Conforme:**
   - Suite completa de `pytest` ejecutada en base SQLite temporal (`tmp_path`).
   - Cobertura de casos válidos, inválidos (422), duplicados (409), ajenos (404) y sin autorización (401).
   - Servidor arrancable mediante `uvicorn backend.la_estrellita.main:create_app --factory --reload`.
3. **Frontend Conforme:**
   - Compilación limpia de TypeScript sin errores (`tsc --noEmit`).
   - Verificación de navegación por teclado completa sin trampas de foco.
   - Verificación con NVDA en Windows confirmando lectura correcta de formularios, tablas y alertas.
4. **Integridad del Repositorio:**
   - Los archivos de `referencias/` permanecen idénticos a los del profesor.
   - Cero credenciales o secretos en Git (archivo `.env` en `.gitignore`).

---

## 8. Contradicciones Resueltas

Durante esta etapa de especificación se detectaron y resolvieron formalmente las siguientes discrepancias:

| Discrepancia Previa | Regla Definitiva Adoptada | Justificación Técnica / Pedagógica |
|---|---|---|
| **Campos fiscales y de inventario:** En la exploración inicial se consideraron RFC, dirección y stock. | **Campos mínimos:** Proveedor (`nombre`, `contacto`, `telefono`) y Producto (`codigo`, `nombre`, `categoria`, `precio_centavos`). | La directiva exige explícitamente evitar sobrecarga de datos personales o fiscales y mantenerse proporcional a la enseñanza del curso. |
| **Unicidad global de código vs. unicidad por usuario:** SKU típicamente es global en sistemas tradicionales. | **Unicidad por catálogo (`propietario_id`, `codigo`):** Dos usuarios distintos pueden usar `"P01"`. | Permite aislamiento multiusuario real sin que un usuario bloquee códigos a otros; se implementa con `UniqueConstraint` compuesto en SQLModel. |
| **Política de borrado de proveedores:** En la exploración previa se evaluaron baja lógica y cascada. | **Rechazo estricto `409 Conflict`:** Prohibido borrar proveedores con productos. | Protege la integridad referencial y fuerza al usuario a gestionar conscientemente sus productos asociados. |
| **Autenticación en el proyecto final:** En el turno previo figuraba como duda a consultar con el docente. | **Decisión interna de proyecto:** Se incorpora autenticación completa OAuth2 + JWT con catálogos privados. | Queda formalmente etiquetada como decisión propia de diseño para demostrar dominio técnico de `observatorio_api`. |

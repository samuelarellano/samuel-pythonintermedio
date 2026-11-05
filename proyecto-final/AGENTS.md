# AGENTS.md — Reglas del Proyecto: La Estrellita

Este documento define las directivas operativas, convenciones arquitectónicas y restricciones técnicas para cualquier agente o desarrollador que trabaje en el proyecto final **La Estrellita**.

---

## 1. Identidad y Filosofía de Desarrollo

- **Harness y Rol:** Operamos bajo la disciplina de *el Gentleman* y desarrollo guiado por especificaciones (SDD/ODD).
- **Criterio de Diseño:** Arquitectura limpia proporcional al problema. Conceptos antes que código. Prohibida la sobreingeniería:
  - **No** microservicios.
  - **No** CQRS ni Event Sourcing.
  - **No** buses de eventos asíncronos ni colas distribuidas.
  - **No** patrones de repositorio genérico abstracto que dupliquen o escondan las capacidades de SQLModel/SQLAlchemy.
- **Respeto a las Referencias:** Prohibido modificar o alterar los ejemplos del profesor ubicados en `referencias/` (`biblioteca_aula`, `cafeteria_campus`, `observatorio_api`). Se preservan las atribuciones y licencias al reutilizar código o patrones.
- **Entorno Local y Entrega:** No realizar `git push` ni despliegues remotos. Todas las comprobaciones se ejecutan en local.

---

## 2. Tecnologías y Versiones Oficiales

Alineadas estrictamente con las convenciones verificadas en el curso de Python Intermedio:

### Backend
- **Python:** 3.10 o superior (compatible con Python 3.14 en Windows).
- **Framework:** `FastAPI` (rango `>=0.115,<1.0`, verificado `0.143.0`).
- **Validación y Configuración:**
  - `Pydantic` v2 (`>=2.9,<3.0`, verificado `2.14.0`).
  - `pydantic-settings` (`>=2.7,<3.0`, verificado `2.16.2`).
- **ORM / Persistencia:** `SQLModel` (`>=0.0.24,<0.1`, verificado `0.0.48`, con SQLAlchemy 2.x).
- **Base de Datos:** SQLite local con foreign keys activadas explícitamente (`PRAGMA foreign_keys=ON`).
- **Servidor ASGI:** `Uvicorn` (`>=0.30,<1.0`, verificado `0.54.0`).
- **Seguridad (si aplica):** `PyJWT` (`>=2.10,<3.0`), `pwdlib[argon2]` (`>=0.2,<1.0`), `python-multipart` (`>=0.0.20,<1.0`).
- **Pruebas Backend:** `pytest` (`>=8,<10`), `httpx` (`>=0.27,<1.0`).

### Frontend
- **Framework / Runtime:** React 18/19 con TypeScript estricto.
- **Build Tool:** Vite (puerto estándar local `http://localhost:5173`, habilitado en CORS por defecto).
- **Estilos:** CSS limpio / accesible sin dependencias pesadas innecesarias.

---

## 3. Convenciones de Código y Arquitectura Backend

1. **Application Factory:**
   - La aplicación debe instanciarse mediante una función factory `create_app(settings: Settings | None = None) -> FastAPI`.
   - El ciclo de vida (`lifespan`) maneja la creación de tablas con `SQLModel.metadata.create_all(engine)` y el cierre limpio de conexiones con `engine.dispose()`.

2. **Configuración Tipada:**
   - Toda variable externa proviene de `Settings(BaseSettings)` con lectura de `.env`.
   - Se validan valores críticos (por ejemplo, rechazar secretos triviales o que comiencen con `"REEMPLAZAR"`).

3. **Separación Estricta: Tablas vs. Contratos HTTP:**
   - `models.py`: Únicamente clases con `SQLModel, table=True` representando la persistencia en base de datos.
   - `schemas.py`: Clases `BaseModel` de Pydantic para entrada y salida HTTP:
     - `ConfigDict(extra="forbid", str_strip_whitespace=True)` en esquemas de creación/actualización.
     - `ConfigDict(from_attributes=True)` en esquemas de respuesta pública.
     - En esquemas de actualización parcial (`PATCH`), rechazar `null` explícito (`@field_validator`) si la semántica del dominio exige omitir el campo para conservarlo.

4. **Persistencia y Sesiones:**
   - SQLite configurado con `connect_args={"check_same_thread": False}`.
   - Listener de conexión SQLAlchemy para ejecutar obligatoriamente `PRAGMA foreign_keys=ON`.
   - Sesión inyectada por dependencia `get_session(request: Request)` vía `Depends`.
   - Los commits son explícitos (`session.commit()`); el generador de la sesión no hace auto-commit.

5. **Reglas de Negocio y Precios:**
   - Los montos monetarios se almacenan como enteros en centavos (`precio_centavos: int`) para eliminar inconsistencias de coma flotante.
   - La capa de presentación es responsable de formatear los centavos a moneda visual ($ MXN).

6. **Manejo de Errores y HTTP:**
   - Respuestas estándar: 200 (OK), 201 (Creado), 204 (Eliminado sin cuerpo), 400/422 (Validación/Contrato inválido), 404 (No encontrado / Recurso inexistente o no autorizado), 409 (Conflicto de unicidad).
   - Middleware de trazabilidad HTTP que inyecta `X-Request-ID` (UUID4) y `X-Process-Time` en cada respuesta.
   - Endpoint de salud (`/salud`) para comprobación de liveness del proceso.

7. **Pruebas Aisladas (Pytest):**
   - Las pruebas nunca tocan la base de datos de desarrollo ni de producción.
   - Uso obligatorio de la fixture `tmp_path` de pytest para generar bases SQLite temporales efímeras en cada ejecución.
   - Pruebas exhaustivas para casos de éxito (200/201), validación de parámetros (422 en query/path/body), conflictos (409) y recursos inexistentes (404).

---

## 4. Convenciones de Frontend y Accesibilidad (A11y)

1. **Accesibilidad Nativa (WCAG 2.1 AA):**
   - **Navegación completa por teclado:** Cada acción interactiva (botones, enlaces, modales, formularios, tablas) debe ser operable mediante `Tab`, `Shift+Tab`, `Enter`, `Espacio` y `Escape`.
   - **Indicadores de foco visibles:** No remover `outline` sin proporcionar un estilo de foco de alto contraste equivalente.
   - **Compatibilidad con NVDA y lectores de pantalla:**
     - Uso estricto de HTML semántico (`<main>`, `<nav>`, `<header>`, `<footer>`, `<section>`, `<article>`, `<table role="table">`, etc.).
     - Inputs asociados unívocamente a etiquetas `<label htmlFor="...">`.
     - Mensajes de error vinculados mediante `aria-describedby` y `aria-invalid="true"`.
     - Notificaciones dinámicas de éxito/error mediante regiones vivas (`aria-live="polite"` o `role="status"` / `role="alert"`).
     - Textos alternativos descriptivos en elementos gráficos significativos.

2. **Estructura Modular en React + TypeScript:**
   - Componentes funcionales pequeños con responsabilidades claras.
   - Tipado estricto: tipos de frontend sincronizados con los contratos `schemas.py` del backend.
   - Manejo predecible de estados de carga (`loading`), error (`error`) y contenido vacío (`empty state`).

---

## 5. Nomenclatura e Idioma

- **Dominio de Negocio:** En español (`proveedor`, `producto`, `precio_centavos`, `stock`, `razon_social`, `rfc`).
- **Términos Técnicos y Rutas HTTP:** Convenciones estándar de la industria (`/api/v1/...` o `/proveedores`, `/productos`, `offset`, `limite`, `q`, `id`, `created_at`).
- **Artefactos Técnicos:** Código, variables, nombres de archivos y comentarios técnicos en inglés o español técnico coherente con el estilo del curso (`main.py`, `models.py`, `schemas.py`).

---

## 6. Procedimiento ante Incidencias y Decisiones

- Cualquier duda de negocio sobre autenticación, reglas de borrado o alcances de evaluación debe registrarse en la sección de **Decisiones pendientes de confirmar con el profesor** antes de implementar código que comprometa la arquitectura.
- No asumir respuestas unilaterales en bifurcaciones críticas de arquitectura.

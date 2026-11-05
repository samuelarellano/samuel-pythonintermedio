# OpenSpec Project: La Estrellita

## 1. Visión del Proyecto
**La Estrellita** es un sistema web para la gestión integral y consulta de catálogos comerciales, compuesto por proveedores y productos asociados. El sistema ofrece una API REST robusta en Python (FastAPI/SQLModel) y una interfaz de usuario accesible y moderna en React con TypeScript.

## 2. Metodología de Especificación y Diseño (SDD)
El proyecto se rige por especificaciones previas a la implementación:
- **Especificación de Requisitos y Contratos:** Documentada en `openspec/specs/catalogo-la-estrellita.md`.
- **Matriz de Trazabilidad:** Documentada en `openspec/trazabilidad.md`, vinculando cada concepto enseñado por el profesor Emmanuel Pulido con las características de la aplicación y sus pruebas.
- **Seguimiento de Tareas ODD:** Gestionado en `odd/tasks/la-estrellita.md` con espejado en memoria persistente Engram.

## 3. Arquitectura del Sistema
```
┌────────────────────────────────────────────────────────┐
│               Frontend (React + TypeScript)            │
│  - Catálogo interactivo de Proveedores y Productos     │
│  - Navegación por teclado & Soporte NVDA (A11y AA)     │
│  - Consumo tipado de API REST                          │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON (CORS :5173)
┌───────────────────────────▼────────────────────────────┐
│               Backend (FastAPI + SQLModel)             │
│  - Application Factory (create_app con Lifespan)       │
│  - Routers modulares (/proveedores, /productos, /salud)│
│  - Middleware de trazabilidad (X-Request-ID / Latencia)│
│  - Validación estricta con Pydantic v2 (extra="forbid")│
│  - Dependencias de sesión SQLite (PRAGMA foreign_keys) │
└───────────────────────────┬────────────────────────────┘
                            │ SQL / ACID
┌───────────────────────────▼────────────────────────────┐
│              Base de Datos Local (SQLite)              │
│  - Archivo persistente: la_estrellita.db               │
│  - Integridad referencial: Proveedor 1 ──< N Producto  │
└────────────────────────────────────────────────────────┘
```

## 4. Estado del Repositorio y Entorno
- **Raíz Git:** `samuel-pythonintermedio`
- **Subdirectorio de Trabajo:** `proyecto-final`
- **Referencias del Curso:**
  - `referencias/biblioteca_aula/`: Routing básico, tipos, Pydantic, validación 422, tests unitarios con `TestClient`.
  - `referencias/cafeteria_campus/`: Modularización con `APIRouter`, inyección con `Depends`, modelos de negocio con precios en centavos enteros.
  - `referencias/observatorio_api/`: Arquitectura profesional con `create_app`, SQLModel, SQLite con foreign keys, `pydantic-settings`, middleware de trazabilidad, esquemas vs modelos y pruebas con `tmp_path`.
- **Estado de Conservación:** Los tres proyectos de referencia se mantienen intactos y sin modificaciones.

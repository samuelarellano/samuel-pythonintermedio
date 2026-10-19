# Ejemplo FastAPI

Proyecto de práctica basado en el repositorio `pythonintermedioagora`. Contiene
una API mínima con FastAPI y conserva las tareas anteriores del curso de Python
intermedio.

## Actividad

La aplicación crea una instancia de `FastAPI` y expone la ruta `GET /lovers`.
Al consultarla devuelve tres actividades favoritas, cada una con un identificador
y un título:

```json
[
  {"id": 1, "titulo": "Escuchar audiolibros"},
  {"id": 2, "titulo": "Aprender programación en Python"},
  {"id": 3, "titulo": "Salir a caminar y conocer lugares nuevos"}
]
```

FastAPI también genera documentación interactiva automáticamente:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Preparar el proyecto

Desde la carpeta `ejemplofastapi`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Ejecutar la API

```powershell
python -m uvicorn main:app --reload
```

Después abre <http://127.0.0.1:8000/lovers> o ejecuta:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/lovers
```

## Ejecutar la prueba

```powershell
python -m unittest -v test_main.py
```

La prueba comprueba que `/lovers` responde con estado `200` y con las tres
actividades esperadas.

## Archivos del curso

- `main.py`: aplicación FastAPI.
- `test_main.py`: prueba automática de la ruta raíz.
- `requirements.txt`: dependencias del ejemplo.
- `tarea_clase01.py`: tarea de programación orientada a objetos.
- `sistema_biblioteca.py`: sistema de biblioteca de la clase 2.
- `test_sistema_biblioteca.py`: pruebas del sistema de biblioteca.
- `respuestas_fundamentos_backend_APIs_HTTP.md`: actividad de fundamentos.

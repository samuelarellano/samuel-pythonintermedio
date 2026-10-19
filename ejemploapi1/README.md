# Clase 6: primera API con Flask

Esta clase construye una API de gestión de tareas con Flask. El backend y el
frontend están separados para practicar primero las rutas HTTP y los datos
JSON sin mezclar la lógica de la interfaz.

## Estructura

```text
clase 6/
├── backend/
│   └── app.py          # API Flask y persistencia JSON
├── frontend/
│   ├── index.html      # Estructura de la página
│   ├── styles.css      # Estilos
│   └── app.js          # Llamadas HTTP y comportamiento de la interfaz
└── requirements.txt
```

Las tareas se guardan en `backend/tasks.json` después de crear la primera.
Ese archivo es local y se ignora en Git.

## 1. Preparar el proyecto

Desde la carpeta `clase 6`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 2. Iniciar el backend

En una terminal, desde `clase 6`:

```powershell
python backend/app.py
```

La API estará disponible en <http://127.0.0.1:5000>. Flask solo entrega
respuestas JSON; no sirve la página web. `flask-cors` permite que el frontend
local se comunique con este servidor.

## 3. Iniciar el frontend

En una segunda terminal, desde `clase 6`:

```powershell
python -m http.server 5500 --directory frontend
```

Abre <http://127.0.0.1:5500>. Esta página llama a la API usando `fetch`.
La interfaz usa HTML semántico, etiquetas asociadas a sus campos y una región
`aria-live` para comunicar los resultados a lectores de pantalla.

## 4. Acciones de la API

| Método | URL | Uso |
| --- | --- | --- |
| `GET` | `/tasks` | Traer todas las tareas |
| `POST` | `/tasks` | Crear una tarea |
| `PUT` | `/tasks/{id}` | Actualizar una tarea |
| `DELETE` | `/tasks/{id}` | Eliminar una tarea |

Ejemplo de JSON para crear o actualizar:

```json
{
  "title": "Estudiar Flask",
  "description": "Leer los conceptos básicos de rutas",
  "due_date": "2026-10-15"
}
```

Puedes probar las rutas con la interfaz o con una herramienta HTTP. Por
ejemplo, en PowerShell:

```powershell
$body = @{
  title = "Estudiar Flask"
  description = "Practicar una ruta POST"
  due_date = "2026-10-15"
} | ConvertTo-Json

Invoke-RestMethod http://127.0.0.1:5000/tasks `
  -Method Post -ContentType "application/json" -Body $body
```

## 5. Cómo está organizado el backend

1. `app = Flask(__name__)` crea la aplicación.
2. `@app.get`, `@app.post` y `@app.put` conectan una URL con una función.
3. `request.get_json()` lee el cuerpo JSON enviado por el cliente.
4. `jsonify()` convierte los datos de Python en una respuesta JSON.
5. `read_tasks` y `write_tasks` leen y escriben el archivo local.
6. `validate_task_data` comprueba los datos antes de guardarlos.

## Ejercicio para la clase

1. Ejecuta ambos servidores y crea dos tareas desde el frontend.
2. Abre `backend/tasks.json` y observa cómo se guardan.
3. Prueba `GET`, `POST` y `PUT` con una herramienta HTTP.
4. Agrega una ruta `DELETE /tasks/{id}`.
5. Después, mejora la validación para limitar el tamaño del título.

### Actividades resueltas

- La API incorpora `DELETE /tasks/{id}` y devuelve `204 No Content` al eliminar.
- Si el identificador no existe, la ruta devuelve `404 Not Found`.
- El título es obligatorio y admite como máximo 100 caracteres.
- La interfaz incluye un botón para eliminar cada tarea, con confirmación previa.

## Nota didáctica

El archivo JSON es suficiente para practicar HTTP, rutas, JSON y persistencia
sin introducir todavía una base de datos. Este proyecto no está pensado para
varios usuarios ni para producción.

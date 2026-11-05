# Biblioteca del aula

Una API pequeña para practicar **routing, parámetros y validación de datos**.
Continuamos con los libros del ejemplo del repositorio. Solo necesitas funciones,
listas, diccionarios y nociones de tipos de Python. Requiere **Python 3.10 o superior**.

La historia: el grupo quiere consultar su biblioteca, buscar títulos y registrar
nuevos libros. Todos los datos viven en una lista: al reiniciar o recargar el
servidor se pierden los cambios. Ejecuta un solo proceso durante la actividad.

## Archivos

| Archivo | Para qué sirve |
| --- | --- |
| `main.py` | Ejemplo completo para comparar después de intentar la práctica |
| `practica.py` | API inicial con cuatro tareas `TODO` para completar |
| `EJERCICIOS.md` | Actividades progresivas, pistas y criterios de entrega |
| `GUIA_DE_REPASO.md` | Resumen para estudiar los conceptos de la actividad |
| `peticiones.http` | Casos para probar desde un cliente HTTP |
| `test_api.py` | Comprobación automática del comportamiento esperado |
| `parametros_python.py` | Ejemplo ejecutable de parámetros de funciones Python |

## Ejecutar en PowerShell

Desde la raíz del repositorio:

```powershell
cd biblioteca_aula
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Abre **http://127.0.0.1:8000/docs**. Selecciona una operación, pulsa **Try it out**
y después **Execute**. Observa la URL, el cuerpo de la solicitud y la respuesta.

Para trabajar en los ejercicios, detén el servidor con `Ctrl+C` y ejecuta:

```powershell
.\.venv\Scripts\python.exe -m uvicorn practica:app --reload
```

Ejecuta los comandos dentro de `biblioteca_aula` para evitar importar el `main.py`
de la raíz. Si ya tienes un entorno virtual, puedes usar su intérprete.
En macOS/Linux el equivalente es `.venv/bin/python`.

La actividad tiene dos etapas. Primero ejecuta `python parametros_python.py` para
predecir cómo Python recibe argumentos en una función. Después estudia `main.py`,
que muestra cómo FastAPI obtiene y valida entradas HTTP. La práctica arranca desde
el principio: inicio, filtro por título y validaciones
de texto ya funcionan y están comentados para explicarlos en clase. Faltan el límite
de resultados, la validación de páginas, la búsqueda por id y la creación.
Buscar por id y crear devuelven **501** hasta completar sus tareas.

## Qué aprenderás

## Etapa 1: parámetros de funciones Python

Ejecuta `python parametros_python.py`. Identifica argumentos posicionales, por
nombre, valores predeterminados, parámetros solo por nombre, `*args` y `**kwargs`.
Predice las llamadas marcadas antes de ejecutarlas quitando el comentario de una
en una. Una anotación como `edad: int` documenta el tipo esperado, pero una llamada
normal puede pasar una cadena: Python no valida automáticamente las anotaciones.

## Etapa 2: entradas de una API

Una **ruta** combina método HTTP y dirección con una función de Python.
`GET /libros` y `POST /libros` usan la misma dirección y ejecutan funciones distintas.
En este proyecto los decoradores `@app.get` y `@app.post` muestran ese routing
directamente; `APIRouter` puede introducirse después cuando haya más módulos.

| Operación | Entrada | Resultado esperado en la API terminada |
| --- | --- | --- |
| `GET /` | Sin parámetros | Bienvenida, 200 |
| `GET /libros` | Consulta opcional `q` y `limite` | Lista, 200 |
| `GET /libros/{libro_id}` | Parámetro de ruta entero mayor que 0 | Libro, 200; inexistente, 404 |
| `POST /libros` | Cuerpo JSON con título, autor y páginas | Libro con id asignado, 201 |

Ejemplo: en `/libros/2`, `2` identifica un recurso y es un parámetro **de ruta**.
En `/libros?q=python&limite=1`, los valores después de `?` son parámetros **de consulta**.
En un `POST`, el libro completo viaja en el **cuerpo JSON**:

```json
{"titulo": "Mi primer libro", "autor": "Ana", "paginas": 120}
```

`Annotated[int, Path(gt=0)]` indica un entero y una regla sobre el parámetro de ruta.
`Query` declara reglas de consulta; `Field` declara reglas de los campos del modelo
Pydantic. `gt` significa mayor que, `ge` mayor o igual, y `le` menor o igual.
FastAPI convierte y valida la entrada antes de ejecutar la función.

Un **404** significa que el id es válido pero no existe ese libro. Un **422** indica
que la entrada no cumple los tipos o restricciones. En un 422, revisa `detail`:
`loc` señala si el problema está en `path`, `query` o `body` y en qué campo.

Las reglas elegidas miden longitud: un título formado por espacios cumple
`min_length=1`. Tampoco usamos tipos estrictos: algunos valores convertibles,
como `"120"` para páginas, pueden aceptarse. Discutir estas diferencias es un
buen reto posterior; no es necesario resolverlas para completar esta práctica.

## Comprobar el avance

Instala las herramientas opcionales de evaluación, sin necesitar un servidor activo:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

Eso comprueba `main.py`. Para evaluar el trabajo del estudiante en la misma terminal:

```powershell
$env:API_MODULO = "practica"
.\.venv\Scripts\python.exe -m pytest -q
Remove-Item Env:API_MODULO
```

Al principio habrá fallos intencionales en la práctica. Usa el nombre de cada prueba
y su comparación para localizar la tarea pendiente. Cada prueba restaura los datos,
por lo que no necesitas reiniciar manualmente la biblioteca.

## Referencias

Documentación oficial de FastAPI: [parámetros de ruta](https://fastapi.tiangolo.com/tutorial/path-params/),
[validaciones de consulta](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/)
y [campos del cuerpo](https://fastapi.tiangolo.com/tutorial/body-fields/).

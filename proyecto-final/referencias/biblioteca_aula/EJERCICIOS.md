# Completa la biblioteca

La actividad tiene dos etapas. Empieza por **`parametros_python.py`** y después
trabaja en **`practica.py`**. Usa `main.py` como referencia después de intentar
cada reto. Antes de ejecutar una llamada o petición, escribe qué resultado esperas
y por qué; luego comprueba tu predicción.

## Etapa 1 · Argumentos de funciones Python

Ejecuta `python parametros_python.py` y señala qué valores se asignan a cada
parámetro en las llamadas válidas. Para cada llamada comentada, predice si funciona
y qué error produce. Descomenta y ejecuta una por una.

1. ¿Qué argumentos pueden ocupar una posición y cuáles pueden darse por nombre?
2. ¿Qué valor toma `saludo` si se omite? ¿Por qué `formal` solo puede darse por nombre?
3. ¿Qué tipo de objeto reciben `*args` y `**kwargs`?
4. ¿Por qué `saludar_edad("Ana", "muchos")` se ejecuta aunque `edad` tenga anotación `int`?

Guarda una explicación breve de la diferencia entre una anotación de función normal
y la validación que veremos en una ruta FastAPI.

## Etapa 2 · Entradas y validación en FastAPI

`main.py` es el ejemplo completo y comentado. Identifica dónde se declara cada dato:
`libro_id` está en la ruta, `q` y `limite` en la consulta, y los campos del libro en
el cuerpo JSON. `Path`, `Query` y `Field` declaran reglas que FastAPI/Pydantic
comprueban antes de ejecutar la lógica de la ruta.

## 0. Reconoce las rutas

Ejecuta `practica:app` siguiendo el README y prueba `GET /` y `GET /libros`.
Localiza el decorador, método, ruta y función de cada operación.

Explica por qué consultar libros usa 200 y crear uno debería usar 201.
¿Qué diferencia hay entre `GET /libros` y `POST /libros`?

## 1. Valida el cuerpo JSON · TODO 1

Lee `LibroCrear`: título y autor ya muestran cómo usar `Field`. Completa la regla
de páginas siguiendo esos ejemplos. El contrato completo es:

| Campo | Tipo | Regla |
| --- | --- | --- |
| `titulo` | `str` | De 1 a 100 caracteres |
| `autor` | `str` | De 1 a 80 caracteres |
| `paginas` | `int` | Mayor que 0 y menor o igual que 2000 |

Los tres campos son obligatorios. El cliente no tiene que enviar un id.
Pista: `Field(min_length=..., max_length=...)` y `Field(gt=..., le=...)`.

Prueba un POST con `paginas: 0`, otro sin `autor` y otro válido. Los inválidos
deben devolver **422**. El válido todavía devolverá **501** hasta terminar el TODO 4:
eso muestra que la validación ocurre antes de ejecutar la función.

Comprueba solo este paso con `API_MODULO=practica` configurado como en el README:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -k "validacion_body or campos_obligatorios"
```

## 2. Busca y limita resultados · TODO 2

Lee `listar_libros`: `q` ya tiene validación y el ciclo de búsqueda está resuelto.
Explica primero ese código; después añade la validación y aplicación de `limite`.
El comportamiento final debe cumplir lo siguiente:

- `q` es opcional; si se envía, debe medir entre 1 y 50 caracteres.
- `limite` es entero, vale 10 por defecto y admite valores de 1 a 20.
- Busca `q` dentro del título sin distinguir mayúsculas.
- Aplica el límite después de filtrar; si no hay coincidencias, devuelve `[]`.

Pistas: `Annotated[..., Query(...)]`, `.lower()`, un ciclo o comprensión de lista
y `resultados[:limite]`. Si `q` es `None`, conserva todos los libros.

Comprueba: `/libros?q=PYTHON&limite=1` debe devolver solo el libro **2**.
`/libros?q=inexistente` devuelve `[]`, y `/libros?limite=0` devuelve **422**.

```powershell
.\.venv\Scripts\python.exe -m pytest -q -k "filtrar or busqueda or validacion_query"
```

## 3. Encuentra un libro por id · TODO 3

La ruta y la validación del id ya están declaradas. Reemplaza la respuesta 501:
recorre la lista, compara el id y devuelve el diccionario correspondiente.
Si terminas el recorrido sin encontrarlo, lanza `HTTPException` con código **404**
y mensaje **`Libro no encontrado`**.

Pista: coloca el error después del ciclo; el primer libro podría no ser el buscado.

Predice y comprueba `/libros/2`, `/libros/999`, `/libros/abc` y `/libros/0`.
¿Cuáles llegan a ejecutar la función? ¿Por qué 999 produce 404 y abc produce 422?

```powershell
.\.venv\Scripts\python.exe -m pytest -q -k "obtener or inexistente or validacion_path"
```

## 4. Registra un libro · TODO 4

Reemplaza la respuesta 501 en `crear_libro`:

1. Calcula un id sumando 1 al id máximo existente; si la lista está vacía, empieza en 1.
2. Convierte `libro` a diccionario con `libro.model_dump()` y añade el id generado.
3. Guarda el nuevo diccionario en `libros`.
4. Devuelve ese libro. El decorador ya establece el código **201**.

Pistas: `max(..., default=0)`, `append` y desempaquetado de diccionario `**`.
Envía dos libros y comprueba que sus ids son distintos. Después consulta uno por id.

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Entrega

- `practica.py` con los cuatro TODO resueltos y todas las pruebas aprobadas.
- Tres ejemplos de peticiones: una correcta, una con 404 y otra con 422.
- Explicación breve de ruta, consulta y cuerpo usando ejemplos de esta API.
- Una respuesta a: ¿qué pasa con los libros nuevos al reiniciar y por qué?

## Retos opcionales

Escoge uno después de completar la actividad. Añade tus propios casos de prueba:

- Añadir `GET /libros/resumen` con el total de libros. Decláralo antes de
  `/libros/{libro_id}` y explica qué ocurre si inviertes el orden.
- Añadir un filtro por autor que pueda combinarse con `q`.
- Rechazar títulos compuestos solo por espacios y explicar por qué medir longitud
  no era suficiente.
- Añadir `DELETE /libros/{libro_id}` con 404 cuando no exista. Si usas 204 al borrar,
  recuerda que esa respuesta debe ir sin cuerpo.

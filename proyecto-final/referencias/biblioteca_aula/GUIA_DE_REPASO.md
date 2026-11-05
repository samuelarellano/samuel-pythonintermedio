# Guía de repaso: funciones y parámetros de una API

Esta actividad conecta dos ideas: cómo una función de Python recibe argumentos y
cómo una ruta de FastAPI recibe datos de una solicitud HTTP. La primera etapa
repasa Python; la segunda aplica esos conceptos a una API de libros.

## 1. Parámetros de funciones Python

Un **parámetro** es el nombre que aparece en la definición de la función. Un
**argumento** es el valor que se entrega al llamar la función.

```python
def presentar(nombre, saludo="Hola", *, formal=False):
    ...
```

- `nombre` y `saludo` aceptan argumentos posicionales o por nombre.
- `saludo="Hola"` es un valor predeterminado que se usa si no se entrega otro.
- El `*` hace que los parámetros que aparecen después, como `formal`, solo se
  puedan proporcionar por nombre: `presentar("Ana", formal=True)`.
- `*args` reúne argumentos posicionales adicionales en una tupla.
- `**kwargs` reúne argumentos nombrados adicionales en un diccionario.

Las anotaciones como `edad: int` documentan los tipos esperados, pero Python no
valida automáticamente los argumentos de una función normal. Por eso una llamada
puede pasar una cadena donde la anotación dice `int`.

## 2. Rutas y datos HTTP

Una **ruta** combina un método HTTP y un camino. El método indica la acción y la
ruta indica dónde se realiza. Por eso `GET /libros` y `POST /libros` pueden usar el
mismo camino y ejecutar funciones distintas.

| Tipo de dato | Dónde aparece | Ejemplo | Uso habitual |
| --- | --- | --- | --- |
| Parámetro de ruta (*path*) | Dentro del camino | `/libros/2` | Identificar un recurso; `2` es `libro_id` |
| Parámetro de consulta (*query*) | Después de `?`; se separan con `&` | `/libros?q=python&limite=1` | Filtrar, ordenar o limitar resultados |
| Cuerpo (*body*) | En el contenido de la solicitud, normalmente JSON | `{"titulo":"Mi libro","autor":"Ana","paginas":120}` | Enviar datos para crear o modificar un recurso |

En FastAPI, una ruta dinámica se escribe con llaves, por ejemplo
`/libros/{libro_id}`. “Dinámica” describe el segmento variable; el valor sigue
siendo un parámetro de ruta. Una solicitud puede combinar fuentes: en
`/libros/2?formato=resumen`, `2` viene de la ruta y `formato` de la consulta.

## 3. Validación con FastAPI

FastAPI usa las declaraciones de parámetros y modelos para convertir y validar
los datos antes de ejecutar la función de la ruta:

- `Path(...)` establece reglas para parámetros de ruta, como que el id sea mayor
  que cero.
- `Query(...)` establece reglas para parámetros de consulta, como el tamaño de
  `q` o el rango de `limite`.
- `Field(...)` establece reglas para campos de un modelo Pydantic recibido en el
  cuerpo, como longitud del título o cantidad de páginas.

Estas reglas no son equivalentes a una anotación de tipo aislada en una función
normal: FastAPI integra esas declaraciones en el procesamiento de solicitudes.

## 4. Respuestas y errores de la actividad

- **200**: consulta completada correctamente.
- **201**: recurso creado correctamente.
- **404**: la entrada tiene formato válido, pero el recurso no existe; por ejemplo,
  `/libros/999`.
- **422**: uno o más datos no cumplen el tipo o las restricciones; por ejemplo,
  `/libros/abc` si el id debe ser entero, o `?limite=0` si el mínimo es 1.

En el detalle de un error 422, `loc` indica dónde se encontró el dato inválido:
`path`, `query` o `body`. Una búsqueda de título sin coincidencias devuelve una
lista vacía; no es un error porque la solicitud sí se pudo procesar.

## 5. Recorrido de la actividad

1. Ejecuta `parametros_python.py` y predice las llamadas correctas e incorrectas.
2. Lee `main.py` para seguir las rutas completas y comparar parámetros de Python
   con datos HTTP.
3. Resuelve los cuatro TODO de `practica.py` con las pistas de `EJERCICIOS.md`.
4. Usa `/docs` o `peticiones.http` para probar entradas válidas e inválidas.
5. Comprueba que los datos se guardan en memoria: desaparecen al reiniciar el
   servidor.

## 6. Preguntas para autoevaluarte

- ¿Cuál es la diferencia entre parámetro y argumento en una función?
- ¿Qué diferencia hay entre `/libros/2` y `/libros?id=2`?
- ¿Qué dato de una solicitud está en ruta, consulta y cuerpo?
- ¿Por qué `/libros/999` puede devolver 404 y `/libros/abc` 422?
- ¿Por qué FastAPI puede validar una entrada que una función Python normal no
  valida solo por tener una anotación?

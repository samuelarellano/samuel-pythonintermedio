# De una función compartida a una API organizada

La cafetería necesita consultar productos y registrar pedidos. Ya sabemos declarar
rutas, validar datos y guardar diccionarios en listas. Hoy aprenderemos a compartir
parámetros con `Depends` y a agrupar rutas con `APIRouter`.

## 1. Recordemos lo que ya conocemos

Una operación combina método HTTP y ruta: `GET /productos` consulta;
`POST /productos` crea. En `/productos/1`, el identificador va en la ruta.
En `/productos?q=pan&limite=1`, los filtros van en la consulta.
En un POST, el cliente manda un cuerpo JSON validado con un modelo Pydantic.

`Annotated` agrega información a un tipo. `Query` establece reglas de consulta;
`Path`, reglas de ruta; `Field`, reglas para los campos del modelo.
`gt` significa mayor que; `ge`, mayor o igual; `le`, menor o igual.

## 2. El problema que resuelve Depends

Abre `01_depends.py`. Tanto `/productos` como `/bebidas` necesitan recibir una
búsqueda y un límite. Podríamos repetir su declaración en cada función, pero si
la regla del límite cambia, tendríamos que editar varios lugares.

Una **dependencia** es una función que FastAPI ejecuta para obtener algo que otra
función necesita. Aquí devuelve un diccionario con los filtros validados:

```python
def parametros_busqueda(
    q: Annotated[str | None, Query(min_length=1, max_length=50)] = None,
    limite: Annotated[int, Query(ge=1, le=20)] = 10,
):
    return {"q": q, "limite": limite}
```

`q` es opcional y `limite` vale 10 si no se envía. FastAPI lee estos parámetros
desde la consulta aunque estén declarados en la dependencia.

## 3. Cómo recibe el endpoint el resultado

```python
@app.get("/productos")
def listar_productos(filtros: Annotated[dict, Depends(parametros_busqueda)]):
    ...
```

Este fragmento abreviado muestra la declaración; el archivo contiene la función
completa. `filtros` recibe el diccionario que devuelve `parametros_busqueda`.
El cliente manda `q` y `limite`, no un campo llamado `filtros`.

En `Depends(parametros_busqueda)` pasamos la función sin paréntesis. Así FastAPI
puede ejecutarla al atender la petición. Escribir `Depends(parametros_busqueda())`
llama a la función durante la definición y pasa su resultado en lugar de la función.

Para `GET /productos?q=pan&limite=1`, el recorrido es:

1. FastAPI reconoce la ruta y la dependencia.
2. Lee y valida `q` y `limite`.
3. Ejecuta `parametros_busqueda` con esos valores.
4. Entrega `{"q": "pan", "limite": 1}` como `filtros`.
5. El endpoint filtra la lista y devuelve hasta un resultado.

Con `limite=0`, la validación falla con 422 antes de ejecutar el endpoint.
Una llamada normal de Python no activa automáticamente este mecanismo: es FastAPI
quien interpreta `Depends` al atender la solicitud.

## 4. Compruébalo antes de continuar

Ejecuta la etapa 1 con el comando del README. En `/docs` prueba:

| Petición | Qué observar |
| --- | --- |
| `/productos` | Los tres productos iniciales |
| `/productos?q=pan&limite=1` | Solo Pan de elote |
| `/bebidas` | Café y té |
| `/bebidas?q=pan` | Lista vacía, porque el pan es alimento |
| `/productos?limite=0` | 422 por límite inválido |
| `/bebidas?limite=abc` | 422 por tipo inválido |

La dependencia comparte la lectura y validación de entradas. El filtrado sigue
en cada endpoint para que puedas ver la diferencia entre ambos trabajos.

## 5. El problema que resuelve APIRouter

Ahora abre `app/routers/productos.py`. Al crecer la API, agrupamos sus operaciones
por recurso. `APIRouter` permite definir ese grupo en un módulo:

```python
router = APIRouter(prefix="/productos", tags=["Productos"])

@router.get("")
def listar_productos(filtros: Annotated[dict, Depends(parametros_busqueda)]):
    ...
```

Antes usábamos `@app.get`; ahora usamos `@router.get`. Los parámetros, los modelos
y las validaciones se declaran igual. El prefijo y la ruta se combinan:

| Prefijo | Ruta del decorador | Dirección final |
| --- | --- | --- |
| `/productos` | `""` | `/productos` |
| `/productos` | `/bebidas` | `/productos/bebidas` |
| `/productos` | `/{producto_id}` | `/productos/{producto_id}` |
| `/pedidos` | `""` | `/pedidos` |

`tags` agrupa las operaciones en `/docs`; no cambia la dirección.
Usamos `""` para que las rutas de listado sean `/productos` y `/pedidos`.
La ruta fija `/bebidas` aparece antes de `/{producto_id}` para que no se interprete
la palabra `bebidas` como un id entero.

## 6. Registrar los routers en la aplicación

En `app/main.py`:

```python
from fastapi import FastAPI
from app.routers import pedidos, productos

app = FastAPI(title="Cafetería del campus", version="1.0.0")
app.include_router(productos.router)
app.include_router(pedidos.router)
```

`include_router` incorpora las operaciones a la aplicación principal. Importar
el módulo por sí solo no las registra. Usamos `productos.router` y `pedidos.router`
para distinguir las dos variables que tienen el mismo nombre.

Las carpetas contienen `__init__.py` para organizar el código como paquetes de Python.
Ejecuta Uvicorn desde `cafeteria_campus` para que encuentre el paquete `app`.
Los módulos de rutas importan los datos, modelos y dependencias; no necesitan
importar la aplicación principal.

## 7. Cómo trabajan juntos

En `GET /productos?q=café`, `APIRouter` organiza la operación bajo `/productos`.
`Depends` obtiene sus filtros. Son responsabilidades diferentes y pueden usarse
en la misma función.

El módulo de pedidos muestra otro grupo de rutas. En `POST /pedidos`, Pydantic
valida el cuerpo, buscamos el producto en la lista y calculamos:

```python
total_centavos = producto["precio_centavos"] * pedido.cantidad
```

El servidor asigna el id y calcula el total. Un producto válido pero inexistente
produce 404. Una cantidad fuera de 1 a 20 produce 422. El pedido guardado conserva
el total calculado al crearse.

## 8. Errores frecuentes y límites del ejemplo

| Situación | Qué revisar |
| --- | --- |
| Una ruta nueva devuelve 404 | ¿Incluiste su router? ¿Usaste el prefijo correcto? |
| `No module named app` | Ejecuta desde `cafeteria_campus` |
| Puerto ocupado | Detén el otro servidor con `Ctrl+C` |
| Un parámetro devuelve 422 | Revisa `detail`, especialmente `loc`, en la respuesta |
| Los cambios desaparecen | Las listas se reinician al recargar el servidor |

Las validaciones de texto comprueban longitud: una cadena de espacios puede
cumplir `min_length=1`. Los modelos usan la conversión habitual de Pydantic;
algunos valores convertibles, como `"2"` para cantidad, pueden aceptarse.
La categoría es texto libre y `bebida` debe escribirse exactamente así para el filtro.

## 9. Preguntas de repaso

1. ¿Qué función ejecuta FastAPI antes de listar los productos?
2. ¿Qué valor recibe `filtros` y quién lo construye?
3. ¿Por qué Depends recibe la función sin paréntesis?
4. ¿Cómo queda la URL de `@router.get("/{pedido_id}")` con prefijo `/pedidos`?
5. ¿Qué ocurre si omites `include_router(pedidos.router)`?
6. ¿Cuál es la diferencia entre recibir 404 y 422?

Respuestas para revisar después: (1) `parametros_busqueda`; (2) su diccionario,
construido por esa función; (3) para que FastAPI pueda ejecutarla al resolver la
petición; (4) `/pedidos/{pedido_id}`; (5) sus operaciones no quedan registradas;
(6) 404 señala un recurso inexistente y 422 una entrada que falla la validación.

## Fuentes para ampliar la lectura

Esta guía adapta a la cafetería los conceptos de la documentación oficial:
[dependencias](https://fastapi.tiangolo.com/tutorial/dependencies/) y
[APIRouter y aplicaciones con varios archivos](https://fastapi.tiangolo.com/tutorial/bigger-applications/).
Para repasar lo anterior consulta
[validaciones de consulta](https://fastapi.tiangolo.com/tutorial/query-params-str-validations/) y
[campos del cuerpo](https://fastapi.tiangolo.com/tutorial/body-fields/).

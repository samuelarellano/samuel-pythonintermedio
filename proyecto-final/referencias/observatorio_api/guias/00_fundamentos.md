# 0. De Python a HTTP

Lee [la demo completa](../demos/fundamentos.py). Ejecuta `python -m uvicorn demos.fundamentos:app --reload` desde `observatorio_api` y abre `/docs`.

Una petición tiene método, URL, cabeceras y a veces cuerpo. La respuesta tiene estado, cabeceras y cuerpo. FastAPI relaciona método y ruta con una función. Las anotaciones permiten construir el contrato y validar los datos HTTP; Python por sí solo no valida todas las llamadas a funciones anotadas.

`GET /objetos?limite=1` recibe consulta; `POST /objetos` recibe JSON `{"nombre":"Luna"}`. `Objeto` es un modelo Pydantic: describe el cuerpo. `response_model` declara la salida. Un 201 anuncia creación, un 422 señala entrada inválida. En esta demo el POST devuelve el contrato sin almacenarlo; SQL llega en el bloque 2.

`APIRouter` agrupa rutas. `include_router` las incorpora a la aplicación. `Depends(paginacion)` pide a FastAPI resolver una función antes de ejecutar la ruta. Se pasa la función, no su resultado: escribir `Depends(paginacion())` la ejecutaría durante la importación.

Pregunta: ¿quién llama a `paginacion`? FastAPI al resolver la petición. No la llama el estudiante dentro de `listar`.

Pregunta: ¿qué pasa con `?limite=0`? Se devuelve 422 antes de ejecutar la operación; `Query(ge=1)` expresa esa regla. En el detalle del error, `loc` identifica la entrada inválida.

Pregunta: ¿por qué recuperar estos temas? El siguiente proyecto conserva funciones, tipos, modelos, parámetros y errores; agrega recursos persistentes e identidad sin sustituir los fundamentos.

Fuentes: [dependencias](https://fastapi.tiangolo.com/tutorial/dependencies/), [APIRouter y varios archivos](https://fastapi.tiangolo.com/tutorial/bigger-applications/), [cuerpo de la petición](https://fastapi.tiangolo.com/tutorial/body/). Consulta: 2026-10-29. Explicación adaptada, no traducción literal.

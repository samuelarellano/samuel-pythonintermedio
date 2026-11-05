# Cafetería del campus

Proyecto de clase para aprender **Depends** y **APIRouter** sobre lo trabajado
en `biblioteca_aula`: funciones, listas, diccionarios, tipos, rutas, consultas,
cuerpos JSON, modelos Pydantic, validaciones y errores HTTP.
Requiere Python 3.10 o superior.

## Preparar el entorno

Desde la raíz del repositorio, en PowerShell:

```powershell
cd cafeteria_campus
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Etapa 1: Depends en un archivo

```powershell
.\.venv\Scripts\python.exe -m uvicorn 01_depends:app --reload
```

Abre http://127.0.0.1:8000/docs y prueba `/productos` y `/bebidas`.
Ambos reciben `q` y `limite` mediante la misma dependencia. El nombre
`01_depends` funciona como cadena de importación de Uvicorn; no escribas
`import 01_depends` en Python.

## Etapa 2: aplicación con routers

Detén el primer servidor con `Ctrl+C` y ejecuta desde **esta misma carpeta**:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Abre http://127.0.0.1:8000/docs. Verás los grupos Productos y Pedidos.
Usa **Try it out**, completa los campos y pulsa **Execute**.
En macOS/Linux el intérprete del entorno es `.venv/bin/python`.

| Método y ruta | Resultado |
| --- | --- |
| `GET /` | Bienvenida |
| `GET /productos?q=pan&limite=1` | Productos filtrados por nombre |
| `GET /productos/bebidas` | Productos con categoría `bebida` |
| `GET /productos/{producto_id}` | Producto o error 404 |
| `POST /productos` | Crear producto, 201 |
| `GET /pedidos` | Lista de pedidos |
| `GET /pedidos/{pedido_id}` | Pedido o error 404 |
| `POST /pedidos` | Crear pedido y calcular total, 201 |

Ejemplo de producto:

```json
{"nombre": "Chocolate caliente", "categoria": "bebida", "precio_centavos": 4000}
```

Ejemplo de pedido:

```json
{"producto_id": 1, "cantidad": 2}
```

Con los datos iniciales, ese pedido cuesta `7000` centavos ($70.00 MXN).
Cada pedido contiene un solo producto y su cantidad. La categoría es texto libre;
el filtro de bebidas busca exactamente `bebida`. Los precios son enteros en centavos.
Los datos se pierden al reiniciar o recargar el servidor. Usa un solo proceso.

## Material de clase

- [Guía para estudiantes](GUIA_ESTUDIANTES.md): lectura y recorrido del código.
- [Ejercicios](EJERCICIOS.md): actividades con criterios de revisión.
- [Peticiones HTTP](peticiones.http): ejemplos para clientes que admiten `.http`;
  también puedes reproducirlos desde `/docs` sin instalar extensiones.
- `01_depends.py`: ejemplo independiente y completo.
- `app/main.py`: aplicación completa; `app/routers/` contiene sus rutas.
- `app/dependencias.py`: parámetros compartidos; `app/modelos.py`: cuerpos JSON;
  `app/datos.py`: listas compartidas.

Orden sugerido para 90 minutos: 10 de repaso, 25 para Depends, 25 para APIRouter,
20 para ejercicios y 10 para revisar respuestas.

## Fuentes oficiales

- [Dependencias de FastAPI](https://fastapi.tiangolo.com/tutorial/dependencies/).
- [Aplicaciones con varios archivos y APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/).

# Respuestas: Fundamentos del backend, las APIs y HTTP

## 1. Diferencia entre frontend y backend

El **frontend** es la parte de una aplicacion con la que la persona interactua directamente. Incluye elementos como botones, formularios, menus y mensajes que se muestran en una pagina web o aplicacion. El **backend** se ejecuta en un servidor, procesa las solicitudes, aplica reglas y guarda o consulta datos.

Ejemplo: en una aplicacion bancaria, la pantalla donde una persona escribe la cantidad que desea transferir pertenece al frontend. El backend comprueba que la cuenta exista, que haya saldo suficiente, registra la transferencia y devuelve el resultado al frontend.

## 2. Semejanza entre una API y los metodos publicos de una clase

Ambos ofrecen una forma definida de utilizar funciones sin conocer su implementacion interna. Para llamar a un metodo publico se necesita conocer su nombre, sus parametros y lo que devuelve. De manera similar, para consumir una API se necesita conocer el endpoint, el verbo HTTP, los datos que recibe y el formato de su respuesta.

Por ejemplo, al ejecutar `cuenta.depositar(100)` no es necesario saber como se modifica el saldo internamente. Al enviar `POST /depositos` ocurre algo equivalente, aunque la operacion se ejecuta en otro equipo por medio de la red.

## 3. Por que HTTP no tiene memoria y que consecuencia tiene

Se dice que HTTP no tiene memoria porque cada peticion se procesa de forma independiente. El servidor no supone que una peticion nueva pertenece a la misma persona que envio una anterior.

Como consecuencia, cuando una operacion necesita identificar a la persona usuaria, cada peticion debe incluir nuevamente la informacion de autenticacion, normalmente mediante una cookie, un token o el encabezado `Authorization`.

## 4. Diferencia entre PUT y PATCH

`PUT` se utiliza para reemplazar un recurso completo. El cliente envia todos sus campos y los datos omitidos pueden perderse o volver a su valor predeterminado.

`PATCH` se utiliza para modificar solo una parte del recurso. Los campos que no se incluyen permanecen sin cambios.

Ejemplo:

```http
PUT /tareas/5
Content-Type: application/json

{"titulo": "Estudiar HTTP y JSON", "completada": true}
```

```http
PATCH /tareas/5
Content-Type: application/json

{"completada": true}
```

## 5. Por que POST no es idempotente y que problema puede causar

`POST` no es idempotente porque repetir la misma peticion normalmente crea un recurso nuevo en cada intento. Si una aplicacion envia una solicitud para crear una tarea, no recibe la respuesta por un fallo de conexion y vuelve a enviarla, el servidor podria crear dos tareas iguales.

Para reducir ese riesgo se pueden usar identificadores unicos, claves de idempotencia o comprobaciones que detecten duplicados.

## 6. Diferencia entre un error 404 y un error 500

- Ante un **404 Not Found**, primero revisaria el lado del cliente: la URL, la ruta, el verbo HTTP y el identificador solicitado. El recurso o endpoint puede no existir.
- Ante un **500 Internal Server Error**, revisaria el lado del servidor: los registros de errores, excepciones del codigo, configuracion, conexion con la base de datos y servicios dependientes.

## 7. Peticion curl para borrar la tarea con id 3

```bash
curl -i -X DELETE http://localhost:8000/tareas/3
```

La respuesta esperada es `204 No Content` si la tarea existe y se elimina correctamente. Si no existe, la API deberia devolver `404 Not Found`.

## 8. Conversion de un diccionario de Python a JSON

Diccionario de Python:

```python
{"nombre": "Ana", "activa": True, "notas": None}
```

JSON equivalente:

```json
{"nombre": "Ana", "activa": true, "notas": null}
```

En JSON, `True` se escribe `true` y `None` se escribe `null`.

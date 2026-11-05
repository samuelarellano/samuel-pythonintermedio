# Práctica de clase

El proyecto está completo y funcional. Realiza estos cambios como actividades
adicionales después de leer la guía. Prueba cada uno en `/docs`.

## 1. Predecir una dependencia

En la etapa 1, antes de ejecutar `/bebidas?q=pan&limite=1`, escribe qué diccionario
recibirá `filtros` y qué lista responderá el endpoint.

Criterio: distinguir entre el resultado de la dependencia y la respuesta HTTP.
Pista: primero se seleccionan bebidas y después se busca el nombre.

## 2. Cambiar una regla compartida

En `01_depends.py`, cambia el máximo de `limite` de 20 a 5. Prueba `limite=6`
en `/productos` y `/bebidas`.

Criterio: ambos deben responder 422 después de editar una sola declaración.
La aplicación de la etapa 2 tiene su propia dependencia en `app/dependencias.py`;
modificar el archivo independiente no cambia la segunda aplicación.

## 3. Reutilizar Depends en otra ruta

En `app/routers/productos.py`, agrega `GET /productos/alimentos`. Usa
`Depends(parametros_busqueda)` y filtra por categoría `alimento`, nombre y límite.
Declara la ruta antes de `/{producto_id}`.

Criterio: con datos iniciales, `/productos/alimentos?q=pan&limite=1` devuelve
Pan de elote; `limite=0` responde 422. No vuelvas a declarar `q` y `limite`.

## 4. Crear un router

Crea `app/routers/cafeteria.py` con un `APIRouter` de prefijo `/cafeteria` y etiqueta
`Cafetería`. Agrega una operación GET que devuelva el nombre y horario del local.
Impórtalo e inclúyelo en `app/main.py`.

Criterio: `GET /cafeteria` responde 200 y aparece en su propio grupo en `/docs`.
Pista: dentro del router usa `@router.get("")`.

## 5. Recorrer un pedido

Crea un pedido de tres unidades del producto 1. Consulta el pedido por el id
devuelto y luego intenta crear otro con `producto_id=999`.

Criterio: el primer POST responde 201 y total de 10500 centavos; el GET responde
200; el producto inexistente produce 404 sin agregar pedidos.
Prueba también `cantidad=0`: debe producir 422.

## Entrega

Presenta el código modificado y ejemplos de peticiones con sus respuestas.
Explica con tus palabras qué comparte Depends, qué organiza APIRouter y para qué
sirve include_router. Comprueba que las operaciones originales siguen funcionando.

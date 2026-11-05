# 1. Middleware: rodear una petición

Ejecuta `python -m uvicorn demos.middleware:app --reload`. Lee [middleware.py](../demos/middleware.py). Consulta `GET /saludo` y `GET /error` en `/docs`; despliega las cabeceras de respuesta.

El middleware ejecuta código antes y después de pedir la respuesta al siguiente componente mediante `await call_next(request)`. Sirve para comportamiento transversal, por ejemplo correlación de peticiones y medición. `request.state` comparte un dato durante esa petición; no es un almacén global de usuarios.

El ejemplo crea `X-Request-ID` y `X-Process-Time`. El primero identifica la petición; el segundo expresa segundos medidos con un reloj monotónico. No incluye necesariamente toda la descarga de una respuesta en streaming. Una excepción HTTP controlada se convierte en respuesta: también observarás las cabeceras en el 404 de `/error`. Una excepción inesperada puede ser procesada por una capa externa y no recorrer el código posterior a `call_next` de este middleware.

Pregunta: ¿middleware y Depends son intercambiables? No. Una dependencia resuelve necesidades de rutas concretas (usuario o sesión) y se integra con su contrato. El middleware rodea el procesamiento HTTP. La autenticación de este proyecto usa dependencias.

Pregunta: ¿qué orden tienen dos middleware? El último agregado es el más externo: entra primero y sale al final. Al agregar A y después B, el recorrido normal es B → A → ruta → A → B.

En la API integrada, [astro/middleware.py](../astro/middleware.py) registra identificador, método, estado y duración, sin cuerpos ni tokens. [main.py](../astro/main.py) configura CORS para un origen explícito. CORS es una política del navegador; no autentica clientes. `expose_headers` permite al JavaScript del origen autorizado leer las cabeceras personalizadas.

Pregunta: ¿un curl queda protegido por CORS? No. Un cliente fuera del navegador puede llamar a la API; el control real de acceso depende del token y de la propiedad del recurso.

La dependencia de sesión usa `yield` para cerrar recursos. No debes deducir su instante exacto de cierre solo de este diagrama: FastAPI distingue alcances de dependencias y respuestas en streaming. Aquí no dependemos de ese orden para confirmar escrituras; hacemos commit antes de devolver el resultado.

Fuentes: [middleware](https://fastapi.tiangolo.com/tutorial/middleware/), [CORS](https://fastapi.tiangolo.com/tutorial/cors/), [dependencias con yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/). Consulta: 2026-10-29.

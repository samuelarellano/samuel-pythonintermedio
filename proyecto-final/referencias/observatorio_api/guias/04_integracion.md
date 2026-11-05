# 4. Seguir una petición por la API completa

La aplicación es una bitácora privada. Una persona se registra, inicia sesión y administra observaciones de objetos del cielo. Dos usuarios pueden observar Saturno sin compartir sus registros.

| Componente | Responsabilidad |
| --- | --- |
| `astro/main.py` | Construir app, lifespan, middleware, CORS y routers |
| `config.py` | Validar variables de entorno |
| `models.py` | Tablas Usuario y Observacion |
| `schemas.py` | Entradas y salidas HTTP |
| `database.py` | Engine y sesión por petición |
| `security.py` | Hash y verificación/emisión JWT |
| `dependencies.py` | Resolver identidad y sesión |
| `routers/auth.py` | Registro, token y perfil |
| `routers/observaciones.py` | CRUD y propiedad del recurso |

Recorrido de `POST /observaciones`: middleware asigna un id → FastAPI valida JSON y resuelve dependencias → OAuth2PasswordBearer extrae el token → se valida firma y exp → se consulta Usuario → la ruta añade propietario_id → Session confirma → response_model filtra salida → middleware añade cabeceras. Si hay validación inválida, la ruta no se ejecuta.

Pregunta: ¿la sesión del usuario y la de la ruta son distintas? No en esta petición: ambas dependen de la misma función y FastAPI reutiliza el resultado por defecto. Otra petición obtiene otra sesión.

El arranque usa `lifespan` para inicializar tablas; al apagar, libera el engine. Usamos una fábrica `create_app` para inyectar configuración en pruebas sin cargar secretos de clase. No se abre un servidor al importar archivos.

Las operaciones SQL y el hash son síncronos; las rutas se declaran con `def` para que FastAPI las ejecute en su pool de hilos. El middleware usa `async def` porque espera `call_next`. Declarar una función async no convierte automáticamente una consulta bloqueante en no bloqueante.

Pregunta: ¿por qué no añadir una capa repository y una clase service por tabla? No son requisitos de FastAPI. Con estas reglas pequeñas aportarían indirección; cuando haya transacciones o reglas compartidas entre operaciones, convendrá extraer funciones o servicios con responsabilidades reales.

La respuesta pública del registro tiene id y username. `password_hash` existe en la tabla pero no en el contrato público. Una contraseña se envía solo a registro/login y nunca se registra en logs. Las observaciones se listan filtrando propietario y se buscan usando id más propietario; la misma comprobación protege GET, PATCH y DELETE.

Pregunta: ¿puede otra persona adivinar un id? Sí, los ids no son secretos. El permiso depende del filtro de propiedad, no de la dificultad de adivinar el número.

Lee después [criterio profesional](05_criterio_profesional.md) y ejecuta el recorrido del README.

Fuentes: [aplicaciones grandes](https://fastapi.tiangolo.com/tutorial/bigger-applications/), [lifespan](https://fastapi.tiangolo.com/advanced/events/), [response_model](https://fastapi.tiangolo.com/tutorial/response-model/), [async y def](https://fastapi.tiangolo.com/async/). Consulta: 2026-10-29.

# 5. Del código organizado al criterio profesional

La base incluye configuración validada, contratos públicos, transacciones explícitas, hash Argon2, tokens con caducidad, control de propiedad, sesiones por petición, logs sin credenciales y pruebas. Esto permite estudiar decisiones profesionales con una aplicación pequeña; no equivale a una plataforma de producción terminada.

Las pruebas son ejemplos resueltos de comportamiento: usan una base temporal por prueba, una app nueva y un secreto de prueba. TestClient se abre con `with` para ejecutar lifespan. No requieren servidor activo y no tocan `observatorio.db`. Puedes leer cada aserción como una especificación: qué debe pasar y qué información no debe salir.

Pregunta: ¿basta comprobar que devuelve 200? No. Comprobar propiedad exige dos identidades y verificar que la segunda no lista, consulta, modifica ni borra el recurso de la primera. Seguridad también incluye rechazar tokens vencidos, firmados con otra clave o sin claims.

Pregunta: ¿por qué probar persistencia? Una API puede devolver datos correctamente desde memoria y perderlos al reiniciar. La prueba reabre una app contra el mismo archivo temporal para verificar que la fila sobrevive.

Para evolucionar: migraciones versionadas con Alembic; PostgreSQL cuando las necesidades de concurrencia lo exijan; secretos administrados y HTTPS en el despliegue; rate limiting y protección ante fuerza bruta; recuperación y verificación de cuentas; política de revocación; proveedor OIDC cuando corresponda; backups con restauración comprobada; health checks de disponibilidad; logs, métricas y alertas; dependencias bloqueadas y revisadas. Son siguientes decisiones de ingeniería, no funciones ya implementadas.

No se implementan roles de administrador, refresh tokens, revocación inmediata, paginación por cursor ni edición concurrente con control de versión. Un PATCH simultáneo puede sobrescribir otro cambio. `/salud` comprueba que el proceso responde, no que la base esté disponible. El middleware mide respuestas procesadas normalmente; no garantiza cabeceras para cualquier 500 inesperado.

Pregunta: ¿migrar a PostgreSQL es cambiar solo una URL? El ORM facilita reutilizar modelos, pero hay que instalar un driver, migrar datos y esquema y revisar tipos, consultas, concurrencia y despliegue. Esa transición necesita pruebas propias.

Fuentes: [pruebas en FastAPI](https://fastapi.tiangolo.com/tutorial/testing/), [dependencias sustituidas en pruebas](https://fastapi.tiangolo.com/advanced/testing-dependencies/), [conceptos de despliegue](https://fastapi.tiangolo.com/deployment/concepts/). Consulta: 2026-10-29.

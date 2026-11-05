# Diseño de la secuencia

Pregunta conductora: ¿cómo pasa una lista pública de observaciones a una API persistente donde cada persona controla sus datos?

Este diseño se define antes de la implementación. Recupera de `biblioteca_aula` tipos, funciones, parámetros, Pydantic, validación y HTTPException; de `cafeteria_campus`, Depends y APIRouter. El destino es una base profesional explicable, sin prometer que una sesión convierte a alguien en experto.

| Orden | Guía | Archivo aislado | Evidencia que explica el docente |
| --- | --- | --- | --- |
| 0 | 00_fundamentos | fundamentos.py | Validación 422 y dependencia compartida |
| 1 | 01_middleware | middleware.py | Cabeceras también en errores HTTP |
| 2 | 02_sqlite | sqlite.py | Crear, consultar, actualizar, eliminar y reiniciar |
| 3 | 03_oauth2_jwt | oauth2_jwt.py | Formulario, hash, token y ruta protegida |
| 4 | 04_integracion | paquete astro | Propiedad de recursos y sesión por petición |
| 5 | 05_criterio_profesional | tests/test_api.py | Aislamiento, errores y límites del diseño |

Estrategia: leer una explicación breve, observar una ejecución completa, seguir la petición por el código y leer la respuesta razonada de cada pregunta. Todo está resuelto: las preguntas son pausas de comprensión, no tareas de programación. Las demostraciones no importan el paquete integrado ni necesitan ejecutar otra demostración.

Propuesta para hoy (150 minutos): 15 de fundamentos, 20 de middleware, 35 de SQL, 35 de seguridad, 35 de integración y 10 de cierre. Para profundizar: segunda sesión de 120 minutos recorriendo consultas, transacciones, pruebas y decisiones de despliegue. La ruta de principiante a criterio avanzado requiere volver a leer y ejecutar, no aumentar la velocidad de la exposición.

Al comenzar, explicar request/response, terminal, entorno virtual y JSON. En cada bloque el docente muestra primero el resultado, después la función y finalmente la abstracción. En integración seguir una petición POST de extremo a extremo. No introducir repositorios abstractos ni servicios vacíos: aquí las reglas caben en rutas pequeñas.

¿Por qué seguridad después de SQL? Porque el estudiante ya entiende de dónde sale el usuario que el token identifica. En la demostración de seguridad se usa un solo usuario en memoria para aislar la mecánica; la integración lo sustituye por una tabla.

Consulta las fuentes oficiales enlazadas en cada guía; las explicaciones son originales y adaptadas al grupo. Documentación consultada: 29 de octubre de 2026.

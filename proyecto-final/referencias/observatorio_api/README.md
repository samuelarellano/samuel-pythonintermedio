# Bitácora del observatorio: FastAPI, SQLite y JWT

Proyecto de clase completo con una temática nueva: observaciones astronómicas privadas. Retoma tipos, funciones, rutas, parámetros, validación, HTTPException, Depends y APIRouter de los proyectos anteriores. Agrega middleware, SQL con SQLite/SQLModel y autenticación OAuth2 con JWT.

Todos los ejemplos están terminados. Hay preguntas con respuestas explicadas en guías y comentarios, sin ejercicios ni archivos por completar. Requiere Python 3.10 o superior. Los comandos siguientes se ejecutan en PowerShell; no necesitas activar el entorno virtual.

## Preparar y ejecutar

Desde la raíz del repositorio:

```powershell
cd observatorio_api
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Abre `.env` y sustituye el valor completo de `JWT_SECRET` por la salida del último comando. Conserva el secreto entre reinicios y no lo compartas. `.env` y las bases de datos están ignorados en Git. El marcador del ejemplo se rechaza para evitar arrancar con una clave pública. No sobrescribas un `.env` existente al repetir la instalación.

```powershell
.\.venv\Scripts\python.exe -m uvicorn astro.main:create_app --factory --reload
```

Abre [Swagger UI](http://127.0.0.1:8000/docs), [ReDoc](http://127.0.0.1:8000/redoc) o [estado del proceso](http://127.0.0.1:8000/salud). Detén con `Ctrl+C`. Ejecuta siempre desde esta carpeta para resolver imports, `.env` y la ruta de SQLite. En macOS/Linux sustituye `.\.venv\Scripts\python.exe` por `.venv/bin/python`.

Si la creación del entorno falla en `ensurepip` y tu Python global sí tiene pip, puedes completar el entorno sin instalar paquetes globales:

```powershell
python -m venv --system-site-packages --without-pip .venv
python -m pip --python .venv/Scripts/python.exe install -r requirements-dev.txt
```

Para ejecutar solamente la API basta `requirements.txt`; `requirements-dev.txt` añade pytest y httpx. Los rangos permiten actualizaciones compatibles; `requirements-lock.txt` registra las versiones exactas verificadas para reproducir esta entrega.

## Orden de lectura y demostraciones

Empieza por el [diseño didáctico](PLAN_DIDACTICO.md), que explica objetivos, estrategia y tiempos. Cada fila siguiente vincula explicación y código aislado:

| Orden | Guía | Demostración |
| --- | --- | --- |
| 0 | [Fundamentos recuperados](guias/00_fundamentos.md) | [fundamentos.py](demos/fundamentos.py) |
| 1 | [Middleware](guias/01_middleware.md) | [middleware.py](demos/middleware.py) |
| 2 | [SQL y SQLite](guias/02_sqlite.md) | [sqlite.py](demos/sqlite.py) |
| 3 | [OAuth2 y JWT](guias/03_oauth2_jwt.md) | [oauth2_jwt.py](demos/oauth2_jwt.py) |
| 4 | [Integración y arquitectura](guias/04_integracion.md) | [API completa](astro/main.py) |
| 5 | [Criterio profesional](guias/05_criterio_profesional.md) | [Pruebas resueltas](tests/test_api.py) |

Ejecuta una demostración a la vez, deteniendo el servidor anterior. No necesitan `.env` ni la API integrada:

```powershell
.\.venv\Scripts\python.exe -m uvicorn demos.fundamentos:app --reload
.\.venv\Scripts\python.exe -m uvicorn demos.middleware:app --reload
.\.venv\Scripts\python.exe -m uvicorn demos.sqlite:app --reload
.\.venv\Scripts\python.exe -m uvicorn demos.oauth2_jwt:app --reload
```

Cada línea inicia un servidor independiente en el puerto 8000; no pegues las cuatro como un único paso. Usa `/docs` en todas. La demo JWT tiene usuario `luna` y contraseña `CieloDespejado2026!`; el secreto es efímero. La demo SQL guarda en `demo_sqlite.db`; la integrada guarda en `observatorio.db`. No mezcles ambas bases.

## Recorrido completo desde Swagger

1. Ejecuta la API integrada con `--factory`.
2. `POST /auth/registro`: envía `{"username":"luna","password":"CieloDespejado2026!"}`. Obtendrás 201 con id y username. Los nombres aceptan minúsculas, números y guion bajo; las contraseñas requieren de 12 a 128 caracteres. No se recortan sus espacios.
3. Pulsa **Authorize**, escribe esas credenciales y deja vacíos client_id/client_secret. Swagger llama al endpoint de token con un formulario y guarda el Bearer para las rutas protegidas. Alternativamente, `POST /auth/token` permite observar el token, pero ejecutarlo manualmente no autoriza automáticamente Swagger.
4. `GET /auth/yo`: verifica tu identidad, 200.
5. `POST /observaciones`: envía `{"objeto":"Saturno","notas":"Anillos visibles con telescopio"}`. Anota el id de la respuesta 201; no envíes propietario_id.
6. `GET /observaciones?q=Sat&offset=0&limite=20`: muestra únicamente tus observaciones. `GET /observaciones/{id}` obtiene una.
7. `PATCH /observaciones/{id}` con `{"notas":"Noche muy clara"}` conserva objeto. Omitir un campo lo conserva; null explícito devuelve 422.
8. Reinicia y vuelve a consultar: el dato sigue guardado. Con el mismo secreto, un token no vencido sigue funcionando.
9. Registra `sol`, usa Logout y Authorize con esa cuenta. Su lista estará vacía y consultar, editar o borrar el id de luna devuelve 404. Vuelve a autorizar a luna.
10. `DELETE /observaciones/{id}` devuelve 204 sin cuerpo. Consultarlo después devuelve 404.

Pregunta: ¿por qué este recorrido usa dos cuentas? Así se observa la diferencia entre saber quién llama y comprobar qué datos le pertenecen.

## Rutas y errores

| Ruta | Acceso | Resultado normal |
| --- | --- | --- |
| `GET /salud` | Público | 200, proceso activo |
| `POST /auth/registro` | Público, JSON | 201, usuario público |
| `POST /auth/token` | Público, formulario | 200, token Bearer |
| `GET /auth/yo` | Bearer | 200, perfil |
| `GET /observaciones` | Bearer | 200, lista propia con filtro y paginación |
| `POST /observaciones` | Bearer, JSON | 201, observación |
| `GET /observaciones/{id}` | Propietario | 200, observación |
| `PATCH /observaciones/{id}` | Propietario, JSON | 200, observación actualizada |
| `DELETE /observaciones/{id}` | Propietario | 204, sin cuerpo |

401: falta token, token inválido/vencido o credenciales incorrectas. 404: observación inexistente o ajena. 409: nombre de usuario ocupado. 422: contrato inválido, incluido enviar JSON al login. Un token caduca en 30 minutos por defecto; configura `TOKEN_MINUTES` de 1 a 120. Para observar el vencimiento durante clase, usa 1, reinicia, obtiene un token nuevo y espera más de un minuto.

Observa `X-Request-ID` y `X-Process-Time` en respuestas normales y errores HTTP controlados. Un origen CORS permitido no sustituye autenticación. Puedes ajustar `CORS_ORIGINS` en `.env` como lista JSON de orígenes exactos.

## Probar sin Swagger

[peticiones.http](peticiones.http) contiene solicitudes ordenadas para una extensión compatible: copia el access_token y el id a sus variables. También puedes probar desde una segunda terminal PowerShell:

```powershell
$base = "http://127.0.0.1:8000"
$registro = @{ username = "orion"; password = "CieloDespejado2026!" } | ConvertTo-Json
Invoke-RestMethod "$base/auth/registro" -Method Post -ContentType "application/json" -Body $registro
$login = Invoke-RestMethod "$base/auth/token" -Method Post -Body @{ username = "orion"; password = "CieloDespejado2026!" }
$cabeceras = @{ Authorization = "Bearer $($login.access_token)" }
$datos = @{ objeto = "Jupiter"; notas = "Cuatro lunas visibles" } | ConvertTo-Json
$observacion = Invoke-RestMethod "$base/observaciones" -Method Post -Headers $cabeceras -ContentType "application/json" -Body $datos
Invoke-RestMethod "$base/observaciones/$($observacion.id)" -Headers $cabeceras
```

El registro repetido devuelve 409; en ese caso continúa desde login. No necesitas clientes HTTP adicionales.

## Pruebas automáticas

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

No requieren servidor ni `.env`. Cubren registro, duplicados, login, contratos, CRUD, propiedad con dos cuentas, filtros, paginación, tokens inválidos/vencidos, middleware, CORS, persistencia y las cuatro demostraciones. Se usan archivos SQLite temporales; nunca la base de clase. Si tu entorno restringe el directorio temporal de Windows, añade `--basetemp=.test-temp`.

Para empezar otra bitácora sin borrar la actual, detén el servidor y cambia `DATABASE_URL` a `sqlite:///./otra_bitacora.db` en `.env`. No hay datos de ejemplo insertados automáticamente. `create_all` crea tablas ausentes, pero no migra tablas existentes.

## Alcance y fuentes

Esta es una base profesional de enseñanza: no implementa revocación, refresh tokens, roles ni migraciones. El flujo OAuth2 con contraseña reproduce el tutorial para entender sus piezas; RFC 9700 descarta ese grant para sistemas nuevos, donde se debe evaluar OIDC y Authorization Code con PKCE. Lee los límites y la evolución en la guía 5 antes de desplegar.

Verificación de esta entrega: 16 pruebas aprobadas con Python 3.14.7. Starlette 1.7 emite una advertencia de deprecación de su integración con httpx en TestClient; las pruebas siguen funcionando. El archivo de versiones fija ese entorno verificado; los rangos de requirements permiten resolver versiones adecuadas para otras versiones de Python.

Las guías enlazan documentación oficial de FastAPI y SQLModel, consultada el 29 de octubre de 2026, con explicaciones propias. Referencias principales: [SQL](https://fastapi.tiangolo.com/tutorial/sql-databases/), [JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), [middleware](https://fastapi.tiangolo.com/tutorial/middleware/) y [APIRouter](https://fastapi.tiangolo.com/tutorial/bigger-applications/).

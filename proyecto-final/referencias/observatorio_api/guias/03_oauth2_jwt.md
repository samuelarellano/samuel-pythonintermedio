# 3. Autenticación, OAuth2 y JWT

Ejecuta `python -m uvicorn demos.oauth2_jwt:app --reload`. Lee [oauth2_jwt.py](../demos/oauth2_jwt.py). En `/docs`, usa Authorize con usuario `luna` y contraseña `CieloDespejado2026!`; deja los campos de cliente vacíos. Después consulta `/yo`.

Autenticar es identificar al solicitante. Autorizar es decidir qué puede hacer. OAuth2 describe flujos de autorización y entrega de tokens; JWT es un formato que podemos usar para esos tokens. Bearer significa que quien presenta el token puede usarlo: hay que protegerlo durante transporte y almacenamiento.

Siguiendo el tutorial de FastAPI, esta clase muestra el flujo de contraseña: el cliente envía `username` y `password` como formulario `application/x-www-form-urlencoded`. `OAuth2PasswordRequestForm` interpreta ese formulario; no recibe JSON. Tras verificar credenciales, la API devuelve `access_token` y `token_type`. El cliente manda `Authorization: Bearer <token>` en las siguientes peticiones.

Este flujo se conserva para comprender la mecánica del tutorial en el aula. La práctica vigente de OAuth2 (RFC 9700, sección 2.4) establece que el grant de contraseña no debe usarse en sistemas nuevos. Para ellos, evaluar un proveedor OAuth2/OIDC y Authorization Code con PKCE; esta API no implementa un proveedor completo ni inicio de sesión con Google.

El hash Argon2 de `pwdlib` permite verificar contraseñas sin guardarlas como texto plano. Tiene salt y coste de trabajo. Un hash no se descifra: se verifica una candidata. El JWT sí contiene datos legibles: cabecera, payload y firma. Firmar protege integridad; no cifra contenido. Nunca metas contraseñas en el token.

`sub` identifica al sujeto; en la API integrada es el id estable del usuario convertido a cadena. `iat` indica emisión y `exp` vencimiento, con fechas UTC. `jwt.decode` verifica firma y vencimiento usando una lista fija de algoritmos. Requerimos también la presencia de esos claims. Leer un payload sin verificar firma no autentica a nadie.

Pregunta: ¿`OAuth2PasswordBearer` valida el JWT? No: extrae la credencial Bearer y documenta el esquema OpenAPI. Nuestra dependencia verifica el JWT y consulta al usuario. Un token válido de un usuario eliminado se rechaza.

Pregunta: ¿cuándo aparece 401? Ante falta de identidad válida: token ausente, alterado, vencido o sujeto desconocido. La respuesta incluye `WWW-Authenticate: Bearer`. Un 403 sería identidad reconocida sin permiso; aquí los recursos ajenos devuelven 404 para no revelar su existencia.

La demo genera un secreto aleatorio al arrancar: reiniciar invalida sus tokens. La API integrada exige `JWT_SECRET` externo y estable entre reinicios. Cambiarlo invalida todos los tokens existentes. No existe logout con revocación ni refresh token en este ejemplo: un token emitido sigue siendo válido hasta vencer si el usuario existe y la clave sigue vigente.

Pregunta: ¿por qué no incluir `propietario_id` en el JSON de creación? El usuario podría suplantar a otro. Lo tomamos de la identidad verificada, y el contrato rechaza campos extra.

Fuentes: [OAuth2 con contraseña y JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/), [primeros pasos de seguridad](https://fastapi.tiangolo.com/tutorial/security/first-steps/), [OAuth2 Security Best Current Practice, sección 2.4](https://www.rfc-editor.org/rfc/rfc9700.html#section-2.4). Consulta: 2026-10-29.

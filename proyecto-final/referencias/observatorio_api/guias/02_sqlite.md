# 2. De una lista a una base SQL

Ejecuta `python -m uvicorn demos.sqlite:app --reload`. Lee [sqlite.py](../demos/sqlite.py). Crea `{"nombre":"Saturno"}` mediante POST `/objetos`, anota su id y consulta la lista. Reinicia el servidor: el registro sigue en `demo_sqlite.db`. El archivo se crea en el directorio desde el que ejecutas el comando.

Una tabla tiene columnas y filas. La clave primaria identifica una fila; una clave foránea relaciona tablas. En SQL, una consulta conceptual es `SELECT * FROM objeto ORDER BY id LIMIT 20`. Con SQLModel se expresa mediante `select(Objeto).order_by(Objeto.id).limit(20)`: el ORM transforma expresiones en SQL y enlaza parámetros. Evita construir SQL concatenando texto del usuario.

FastAPI permite elegir la biblioteca de datos. Su tutorial SQL utiliza SQLModel, construido sobre SQLAlchemy y Pydantic. Seguimos esa combinación con SQLite para empezar sin servidor de base de datos. `table=True` declara una tabla; los modelos de entrada y salida no son tablas. Separarlos evita permitir campos internos por accidente.

`engine` representa la conexión con la base y su administración. `Session` es una unidad de trabajo: consulta y rastrea cambios. Se crea una por petición con `with` y `yield`; se cierra incluso si ocurre un error. No compartas una Session global entre peticiones.

Secuencia de creación: construir objeto → `add` → `commit` → `refresh`. `add` incorpora a la unidad de trabajo; `commit` confirma la transacción; `refresh` consulta valores persistidos como el id. Ante un fallo de integridad, `rollback` devuelve la sesión a un estado utilizable. Una sesión cerrada no confirma automáticamente las escrituras.

Pregunta: ¿qué diferencia hay entre PUT y PATCH? La demo reemplaza los datos editables con PUT; la API integrada usa PATCH para modificar solo los campos enviados con `exclude_unset=True`. Allí un campo omitido se conserva y `null` explícito se rechaza.

Pregunta: ¿`check_same_thread=False` vuelve ilimitada la concurrencia? No. Permite usar conexiones SQLite en los hilos que utiliza esta aplicación; SQLite conserva límites de bloqueo y escritura. No autoriza compartir sesiones.

En la integración, `usuario.id` se relaciona con `observacion.propietario_id`. Activamos `PRAGMA foreign_keys=ON` por conexión. La restricción UNIQUE protege nombres de usuario incluso ante registros simultáneos. Los filtros de propiedad restringen consultas antes de devolver datos; la paginación acota el resultado y usa orden estable.

Pregunta: ¿`create_all` actualiza una columna ya creada? No. Inicializa tablas ausentes. Evolucionar esquemas existentes exige migraciones, por ejemplo Alembic, y revisar los cambios antes de aplicarlos.

Puedes inspeccionar la BD sin programas adicionales desde la carpeta del proyecto:

```powershell
python -c "import sqlite3; c=sqlite3.connect('observatorio.db'); print(c.execute('SELECT id, objeto, propietario_id FROM observacion').fetchall()); c.close()"
```

La demo CRUD tiene GET por id, PUT y DELETE además del listado y POST. Respuestas esperadas: 201 al crear, 200 al consultar o editar, 204 sin cuerpo al borrar y 404 para un id inexistente.

Fuentes: [SQL en FastAPI](https://fastapi.tiangolo.com/tutorial/sql-databases/), [tutorial de SQLModel](https://sqlmodel.tiangolo.com/tutorial/), [sesión y dependencia](https://sqlmodel.tiangolo.com/tutorial/fastapi/session-with-dependency/). Consulta: 2026-10-29.

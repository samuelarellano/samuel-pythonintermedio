"""CRUD aislado: python -m uvicorn demos.sqlite:app --reload.

Sin autenticación por intención didáctica; usa demo_sqlite.db, nunca la BD integrada.
"""
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query, Response
from sqlmodel import Field, Session, SQLModel, create_engine, select


class ObjetoDatos(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)


class Objeto(ObjetoDatos, table=True):
    id: int | None = Field(default=None, primary_key=True)


class ObjetoPublico(ObjetoDatos):
    id: int


engine = create_engine("sqlite:///./demo_sqlite.db", connect_args={"check_same_thread": False})


@asynccontextmanager
async def lifespan(app):
    SQLModel.metadata.create_all(engine)
    yield
    engine.dispose()


app = FastAPI(title="Demo: SQLModel y SQLite", lifespan=lifespan)


def sesion():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(sesion)]


def buscar(objeto_id, session):
    objeto = session.get(Objeto, objeto_id)
    if objeto is None:
        raise HTTPException(404, "Objeto no encontrado")
    return objeto


@app.post("/objetos", response_model=ObjetoPublico, status_code=201)
def crear(datos: ObjetoDatos, session: SessionDep):
    objeto = Objeto.model_validate(datos)
    session.add(objeto)
    session.commit()
    session.refresh(objeto)
    return objeto


@app.get("/objetos", response_model=list[ObjetoPublico])
def listar(session: SessionDep, limite: Annotated[int, Query(ge=1, le=100)] = 20):
    return session.exec(select(Objeto).order_by(Objeto.id).limit(limite)).all()


@app.get("/objetos/{objeto_id}", response_model=ObjetoPublico)
def obtener(objeto_id: int, session: SessionDep):
    return buscar(objeto_id, session)


@app.put("/objetos/{objeto_id}", response_model=ObjetoPublico)
def reemplazar(objeto_id: int, datos: ObjetoDatos, session: SessionDep):
    objeto = buscar(objeto_id, session)
    objeto.nombre = datos.nombre
    session.add(objeto)
    session.commit()
    session.refresh(objeto)
    return objeto


@app.delete("/objetos/{objeto_id}", status_code=204)
def eliminar(objeto_id: int, session: SessionDep):
    session.delete(buscar(objeto_id, session))
    session.commit()
    # ¿Cerrar la sesión sustituye commit? No: sin commit no persiste la escritura.
    return Response(status_code=204)

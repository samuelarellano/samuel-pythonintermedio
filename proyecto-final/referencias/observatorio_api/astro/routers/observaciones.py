"""CRUD privado: la propiedad se comprueba en TODAS las operaciones."""
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, Response
from sqlmodel import select

from ..dependencies import SessionDep, UsuarioDep
from ..models import Observacion
from ..schemas import ObservacionActualizar, ObservacionCrear, ObservacionPublica

router = APIRouter(prefix="/observaciones", tags=["Observaciones"])
Id = Annotated[int, Path(gt=0)]


def buscar_propia(session, observacion_id, usuario_id):
    observacion = session.exec(select(Observacion).where(
        Observacion.id == observacion_id, Observacion.propietario_id == usuario_id)).first()
    if observacion is None:
        # ¿Por qué 404 también para recursos ajenos? No revelamos su existencia.
        raise HTTPException(404, "Observación no encontrada")
    return observacion


@router.post("", response_model=ObservacionPublica, status_code=201)
def crear(datos: ObservacionCrear, session: SessionDep, usuario: UsuarioDep):
    observacion = Observacion(**datos.model_dump(), propietario_id=usuario.id)
    session.add(observacion)
    session.commit()
    session.refresh(observacion)
    return observacion


@router.get("", response_model=list[ObservacionPublica])
def listar(session: SessionDep, usuario: UsuarioDep,
           q: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
           offset: Annotated[int, Query(ge=0)] = 0,
           limite: Annotated[int, Query(ge=1, le=100)] = 20):
    consulta = select(Observacion).where(Observacion.propietario_id == usuario.id)
    if q:
        consulta = consulta.where(Observacion.objeto.contains(q, autoescape=True))
    return session.exec(consulta.order_by(Observacion.id).offset(offset).limit(limite)).all()


@router.get("/{observacion_id}", response_model=ObservacionPublica)
def obtener(observacion_id: Id, session: SessionDep, usuario: UsuarioDep):
    return buscar_propia(session, observacion_id, usuario.id)


@router.patch("/{observacion_id}", response_model=ObservacionPublica)
def actualizar(observacion_id: Id, datos: ObservacionActualizar,
               session: SessionDep, usuario: UsuarioDep):
    observacion = buscar_propia(session, observacion_id, usuario.id)
    observacion.sqlmodel_update(datos.model_dump(exclude_unset=True))
    session.add(observacion)
    session.commit()
    session.refresh(observacion)
    return observacion


@router.delete("/{observacion_id}", status_code=204)
def eliminar(observacion_id: Id, session: SessionDep, usuario: UsuarioDep):
    observacion = buscar_propia(session, observacion_id, usuario.id)
    session.delete(observacion)
    session.commit()
    return Response(status_code=204)

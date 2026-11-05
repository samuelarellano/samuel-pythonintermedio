"""Seguridad aislada. Usuario demo: luna / CieloDespejado2026!

python -m uvicorn demos.oauth2_jwt:app --reload
El secreto efímero invalida tokens cuando se reinicia esta demostración.
"""
from datetime import datetime, timedelta, timezone
from secrets import token_hex
from typing import Annotated
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

app = FastAPI(title="Demo: OAuth2 y JWT")
secret = token_hex(32)
hasher = PasswordHash.recommended()
hash_guardado = hasher.hash("CieloDespejado2026!")
oauth2 = OAuth2PasswordBearer(tokenUrl="token")


def error():
    return HTTPException(401, "Credenciales no válidas", headers={"WWW-Authenticate": "Bearer"})


@app.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()]):
    valido = hasher.verify(form.password, hash_guardado)
    if form.username != "luna" or not valido:
        raise error()
    ahora = datetime.now(timezone.utc)
    token = jwt.encode({"sub": "luna", "iat": ahora, "exp": ahora + timedelta(minutes=5)},
                       secret, algorithm="HS256")
    return {"access_token": token, "token_type": "bearer"}


def identidad(token: Annotated[str, Depends(oauth2)]):
    try:
        datos = jwt.decode(token, secret, algorithms=["HS256"],
                           options={"require": ["sub", "iat", "exp"]})
    except InvalidTokenError:
        raise error() from None
    if datos["sub"] != "luna":
        raise error()
    return datos["sub"]


@app.get("/yo")
def perfil(usuario: Annotated[str, Depends(identidad)]):
    # ¿OAuth2PasswordBearer verifica la firma? No, identidad lo hace con jwt.decode.
    return {"username": usuario}

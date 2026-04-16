from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.orm import Usuario, Cliente
from app.security.auth import verify_password, create_access_token

router = APIRouter(prefix="/v1/auth", tags=["Autenticación"])


@router.post("/login")
async def login_usuario(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """Autenticación de usuarios internos (Flask) – devuelve JWT. Ingresa el email en el campo username."""
    user = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    if not user.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario inactivo")

    token_data = {
        "sub": str(user.id),
        "tipo": "usuario",
        "nombre": user.nombre,
        "email": user.email,
        "rol": user.rol.nombre,
        "rol_id": user.rol_id,
        "activo": user.activo,
    }
    access_token = create_access_token(data=token_data)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": user.id,
        "nombre": user.nombre,
        "email": user.email,
        "rol": user.rol.nombre,
        "rol_id": user.rol_id,
    }


@router.post("/login-cliente")
async def login_cliente(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """Autenticación de clientes externos (Laravel) – devuelve JWT. Ingresa el email en el campo username."""
    cliente = db.query(Cliente).filter(Cliente.email == form_data.username).first()
    if not cliente or not verify_password(form_data.password, cliente.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    if not cliente.activo:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cliente inactivo")

    token_data = {
        "sub": str(cliente.id),
        "tipo": "cliente",
        "nombre": cliente.nombre,
        "email": cliente.email,
        "telefono": cliente.telefono,
        "direccion": cliente.direccion,
        "activo": cliente.activo,
    }
    access_token = create_access_token(data=token_data)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "id": cliente.id,
        "nombre": cliente.nombre,
        "email": cliente.email,
        "telefono": cliente.telefono,
        "direccion": cliente.direccion,
    }

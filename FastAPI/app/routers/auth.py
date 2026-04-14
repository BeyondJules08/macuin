from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.orm import Usuario, Cliente
from app.models.usuarios import LoginRequest
from app.models.clientes import ClienteLoginRequest
from app.security.auth import verify_password, create_access_token

router = APIRouter(prefix="/v1/auth", tags=["Autenticación"])


@router.post("/login")
async def login_usuario(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):
    """Autenticación de usuarios internos (Flask) – devuelve JWT"""
    user = db.query(Usuario).filter(Usuario.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
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
        "status": "200",
        "data": {
            "id": user.id,
            "nombre": user.nombre,
            "email": user.email,
            "rol": user.rol.nombre,
            "rol_id": user.rol_id,
            "activo": user.activo,
            "access_token": access_token,
            "token_type": "bearer",
        },
    }


@router.post("/login-cliente")
async def login_cliente(
    credentials: ClienteLoginRequest,
    db: Session = Depends(get_db),
):
    """Autenticación de clientes externos (Laravel) – devuelve JWT"""
    cliente = db.query(Cliente).filter(Cliente.email == credentials.email).first()
    if not cliente or not verify_password(credentials.password, cliente.password_hash):
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
        "status": "200",
        "data": {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "email": cliente.email,
            "telefono": cliente.telefono,
            "direccion": cliente.direccion,
            "activo": cliente.activo,
            "access_token": access_token,
            "token_type": "bearer",
        },
    }

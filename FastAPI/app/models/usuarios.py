from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class RolOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class UsuarioCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    rol_id: int
    activo: bool = True


class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    rol_id: Optional[int] = None
    activo: Optional[bool] = None


class UsuarioOut(BaseModel):
    id: int
    nombre: str
    email: str
    rol_id: int
    rol: Optional[RolOut] = None
    fecha_registro: Optional[datetime] = None
    activo: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

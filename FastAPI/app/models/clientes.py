from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class ClienteCreate(BaseModel):
    nombre: str
    email: EmailStr
    password: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None


class ClienteUpdate(BaseModel):
    nombre: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None


class ClienteOut(BaseModel):
    id: int
    nombre: str
    email: str
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    fecha_registro: Optional[datetime] = None
    activo: bool

    class Config:
        from_attributes = True


class ClienteLoginRequest(BaseModel):
    email: EmailStr
    password: str

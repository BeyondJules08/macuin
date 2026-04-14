from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoriaCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class CategoriaOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True


class InventarioOut(BaseModel):
    id: int
    stock_actual: int
    stock_minimo: int
    fecha_actualizacion: Optional[datetime] = None
    necesita_reposicion: bool = False

    class Config:
        from_attributes = True


class AutoparteCreate(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    categoria_id: int
    marca: Optional[str] = None
    precio: float
    stock_inicial: int = 0
    stock_minimo: int = 0
    activo: bool = True


class AutoparteUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None
    marca: Optional[str] = None
    precio: Optional[float] = None
    activo: Optional[bool] = None


class InventarioUpdate(BaseModel):
    operacion: str  # agregar | restar | establecer
    cantidad: int
    stock_minimo: Optional[int] = None


class AutoparteOut(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None
    categoria_id: int
    categoria: Optional[CategoriaOut] = None
    marca: Optional[str] = None
    precio: float
    activo: bool
    stock_disponible: int = 0
    inventario: Optional[InventarioOut] = None

    class Config:
        from_attributes = True

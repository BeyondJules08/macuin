from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EstadoPedidoOut(BaseModel):
    id: int
    nombre: str

    class Config:
        from_attributes = True


class DetallePedidoCreate(BaseModel):
    autoparte_id: int
    cantidad: int


class DetallePedidoOut(BaseModel):
    id: int
    autoparte_id: int
    autoparte_nombre: Optional[str] = None
    cantidad: int
    precio_unitario: float
    subtotal: float = 0.0

    class Config:
        from_attributes = True


class PedidoCreate(BaseModel):
    usuario_id: int
    items: List[DetallePedidoCreate]


class PedidoExternoCreate(BaseModel):
    cliente_id: int
    items: List[DetallePedidoCreate]
    notas: Optional[str] = None


class PedidoCambioEstado(BaseModel):
    estado_id: int


class PedidoOut(BaseModel):
    id: int
    usuario_id: int
    usuario_nombre: Optional[str] = None
    estado_id: int
    estado_nombre: Optional[str] = None
    fecha_pedido: Optional[datetime] = None
    total: float
    detalles: List[DetallePedidoOut] = []

    class Config:
        from_attributes = True


class PedidoExternoOut(BaseModel):
    id: int
    cliente_id: int
    cliente_nombre: Optional[str] = None
    estado_id: int
    estado_nombre: Optional[str] = None
    fecha_pedido: Optional[datetime] = None
    total: float
    notas: Optional[str] = None
    detalles: List[DetallePedidoOut] = []

    class Config:
        from_attributes = True

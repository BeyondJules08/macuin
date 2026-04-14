from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.data.db import get_db
from app.data.orm import (
    Pedido, DetallePedido, PedidoExterno, DetallePedidoExterno,
    Autoparte, EstadoPedido, Usuario, Cliente
)
from app.models.pedidos import PedidoCreate, PedidoExternoCreate, PedidoCambioEstado
from app.security.auth import get_current_subject

router = APIRouter(prefix="/v1/pedidos", tags=["Pedidos"])


def _serialize_detalle(d) -> dict:
    return {
        "id": d.id,
        "autoparte_id": d.autoparte_id,
        "autoparte_nombre": d.autoparte.nombre if d.autoparte else None,
        "cantidad": d.cantidad,
        "precio_unitario": float(d.precio_unitario),
        "subtotal": float(d.cantidad * d.precio_unitario),
    }


def _serialize_pedido(p: Pedido) -> dict:
    return {
        "id": p.id,
        "usuario_id": p.usuario_id,
        "usuario_nombre": p.usuario.nombre if p.usuario else None,
        "estado_id": p.estado_id,
        "estado_nombre": p.estado.nombre if p.estado else None,
        "fecha_pedido": p.fecha_pedido.isoformat() if p.fecha_pedido else None,
        "total": float(p.total),
        "tipo": "interno",
        "detalles": [_serialize_detalle(d) for d in p.detalles],
    }


def _serialize_pedido_externo(p: PedidoExterno) -> dict:
    return {
        "id": p.id,
        "cliente_id": p.cliente_id,
        "cliente_nombre": p.cliente.nombre if p.cliente else None,
        "estado_id": p.estado_id,
        "estado_nombre": p.estado.nombre if p.estado else None,
        "fecha_pedido": p.fecha_pedido.isoformat() if p.fecha_pedido else None,
        "total": float(p.total),
        "notas": p.notas,
        "tipo": "externo",
        "detalles": [_serialize_detalle(d) for d in p.detalles],
    }


# ── Pedidos internos ──────────────────────────────────────────────────

@router.get("/")
async def listar_pedidos(
    db: Session = Depends(get_db),
    _claims: dict = Depends(get_current_subject),
    usuario_id: Optional[int] = Query(None),
    estado_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    q = db.query(Pedido)
    if usuario_id:
        q = q.filter(Pedido.usuario_id == usuario_id)
    if estado_id:
        q = q.filter(Pedido.estado_id == estado_id)
    total = q.count()
    items = q.order_by(Pedido.fecha_pedido.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "status": "200",
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "data": [_serialize_pedido(p) for p in items],
    }


@router.get("/{id}")
async def obtener_pedido(id: int, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    p = db.query(Pedido).filter(Pedido.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    return {"status": "200", "data": _serialize_pedido(p)}


@router.post("/")
async def crear_pedido(payload: PedidoCreate, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    if not db.query(Usuario).filter(Usuario.id == payload.usuario_id).first():
        raise HTTPException(status_code=400, detail="Usuario no encontrado")

    estado_pendiente = db.query(EstadoPedido).filter(EstadoPedido.nombre == "Pendiente").first()
    if not estado_pendiente:
        raise HTTPException(status_code=500, detail="Estado 'Pendiente' no configurado")

    if not payload.items:
        raise HTTPException(status_code=400, detail="El pedido debe tener al menos un producto")

    pedido = Pedido(usuario_id=payload.usuario_id, estado_id=estado_pendiente.id, total=0)
    db.add(pedido)
    db.flush()

    total = 0.0
    for item in payload.items:
        a = db.query(Autoparte).filter(Autoparte.id == item.autoparte_id, Autoparte.activo == True).first()
        if not a:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Autoparte {item.autoparte_id} no encontrada")
        if not a.inventario or a.inventario.stock_actual < item.cantidad:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para '{a.nombre}'")
        detalle = DetallePedido(
            pedido_id=pedido.id,
            autoparte_id=a.id,
            cantidad=item.cantidad,
            precio_unitario=a.precio,
        )
        a.inventario.stock_actual -= item.cantidad
        total += float(a.precio) * item.cantidad
        db.add(detalle)

    pedido.total = total
    db.commit()
    db.refresh(pedido)
    return {"status": "201", "mensaje": "Pedido creado", "data": _serialize_pedido(pedido)}


@router.put("/{id}/estado")
async def cambiar_estado_pedido(
    id: int, payload: PedidoCambioEstado, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)
):
    p = db.query(Pedido).filter(Pedido.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pedido no encontrado")
    if not db.query(EstadoPedido).filter(EstadoPedido.id == payload.estado_id).first():
        raise HTTPException(status_code=400, detail="Estado no encontrado")
    p.estado_id = payload.estado_id
    db.commit()
    db.refresh(p)
    return {"status": "200", "mensaje": "Estado actualizado", "data": _serialize_pedido(p)}


# ── Pedidos externos (clientes Laravel) ──────────────────────────────

@router.get("/externos/")
async def listar_pedidos_externos(
    db: Session = Depends(get_db),
    _claims: dict = Depends(get_current_subject),
    cliente_id: Optional[int] = Query(None),
    estado_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    q = db.query(PedidoExterno)
    if cliente_id:
        q = q.filter(PedidoExterno.cliente_id == cliente_id)
    if estado_id:
        q = q.filter(PedidoExterno.estado_id == estado_id)
    total = q.count()
    items = q.order_by(PedidoExterno.fecha_pedido.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "status": "200",
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "data": [_serialize_pedido_externo(p) for p in items],
    }


@router.get("/externos/{id}")
async def obtener_pedido_externo(id: int, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    p = db.query(PedidoExterno).filter(PedidoExterno.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pedido externo no encontrado")
    return {"status": "200", "data": _serialize_pedido_externo(p)}


@router.post("/externos/")
async def crear_pedido_externo(
    payload: PedidoExternoCreate, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)
):
    if not db.query(Cliente).filter(Cliente.id == payload.cliente_id).first():
        raise HTTPException(status_code=400, detail="Cliente no encontrado")

    estado_pendiente = db.query(EstadoPedido).filter(EstadoPedido.nombre == "Pendiente").first()
    if not estado_pendiente:
        raise HTTPException(status_code=500, detail="Estado 'Pendiente' no configurado")

    if not payload.items:
        raise HTTPException(status_code=400, detail="El pedido debe tener al menos un producto")

    pedido = PedidoExterno(
        cliente_id=payload.cliente_id,
        estado_id=estado_pendiente.id,
        total=0,
        notas=payload.notas,
    )
    db.add(pedido)
    db.flush()

    total = 0.0
    for item in payload.items:
        a = db.query(Autoparte).filter(Autoparte.id == item.autoparte_id, Autoparte.activo == True).first()
        if not a:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Autoparte {item.autoparte_id} no encontrada")
        if not a.inventario or a.inventario.stock_actual < item.cantidad:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Stock insuficiente para '{a.nombre}'")
        detalle = DetallePedidoExterno(
            pedido_externo_id=pedido.id,
            autoparte_id=a.id,
            cantidad=item.cantidad,
            precio_unitario=a.precio,
        )
        a.inventario.stock_actual -= item.cantidad
        total += float(a.precio) * item.cantidad
        db.add(detalle)

    pedido.total = total
    db.commit()
    db.refresh(pedido)
    return {"status": "201", "mensaje": "Pedido externo creado", "data": _serialize_pedido_externo(pedido)}


@router.put("/externos/{id}/estado")
async def cambiar_estado_pedido_externo(
    id: int, payload: PedidoCambioEstado, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)
):
    p = db.query(PedidoExterno).filter(PedidoExterno.id == id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pedido externo no encontrado")
    p.estado_id = payload.estado_id
    db.commit()
    db.refresh(p)
    return {"status": "200", "mensaje": "Estado actualizado", "data": _serialize_pedido_externo(p)}


# ── Estados ───────────────────────────────────────────────────────────

@router.get("/estados/")
async def listar_estados(db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    estados = db.query(EstadoPedido).all()
    return {
        "status": "200",
        "data": [{"id": e.id, "nombre": e.nombre} for e in estados],
    }

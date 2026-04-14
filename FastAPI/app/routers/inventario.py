from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.data.db import get_db
from app.data.orm import Inventario, Autoparte
from app.models.autopartes import InventarioUpdate
from app.security.auth import get_current_subject

router = APIRouter(prefix="/v1/inventario", tags=["Inventario"])


def _serialize(inv: Inventario) -> dict:
    a = inv.autoparte
    return {
        "id": inv.id,
        "autoparte_id": inv.autoparte_id,
        "autoparte_nombre": a.nombre if a else None,
        "autoparte_marca": a.marca if a else None,
        "autoparte_activo": a.activo if a else None,
        "categoria_nombre": a.categoria.nombre if a and a.categoria else None,
        "stock_actual": inv.stock_actual,
        "stock_minimo": inv.stock_minimo,
        "necesita_reposicion": inv.stock_actual <= inv.stock_minimo,
        "fecha_actualizacion": inv.fecha_actualizacion.isoformat() if inv.fecha_actualizacion else None,
    }


@router.get("/")
async def listar_inventario(
    db: Session = Depends(get_db),
    _claims: dict = Depends(get_current_subject),
    search: Optional[str] = Query(None),
    bajo_stock: bool = Query(False),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    q = db.query(Inventario).join(Autoparte).filter(Autoparte.activo == True)
    if search:
        q = q.filter(
            Autoparte.nombre.ilike(f"%{search}%") | Autoparte.marca.ilike(f"%{search}%")
        )
    if bajo_stock:
        q = q.filter(Inventario.stock_actual <= Inventario.stock_minimo)

    total = q.count()
    items = q.order_by(Autoparte.nombre).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "status": "200",
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "data": [_serialize(i) for i in items],
    }


@router.get("/{id}")
async def obtener_inventario(id: int, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    inv = db.query(Inventario).filter(Inventario.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")
    return {"status": "200", "data": _serialize(inv)}


@router.put("/{id}")
async def actualizar_inventario(
    id: int, payload: InventarioUpdate, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)
):
    inv = db.query(Inventario).filter(Inventario.id == id).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventario no encontrado")

    if payload.operacion == "agregar":
        inv.stock_actual += payload.cantidad
    elif payload.operacion == "restar":
        if inv.stock_actual < payload.cantidad:
            raise HTTPException(status_code=400, detail="Stock insuficiente para restar")
        inv.stock_actual -= payload.cantidad
    elif payload.operacion == "establecer":
        inv.stock_actual = payload.cantidad
    else:
        raise HTTPException(status_code=400, detail="Operación inválida. Use: agregar, restar, establecer")

    if payload.stock_minimo is not None:
        inv.stock_minimo = payload.stock_minimo

    db.commit()
    db.refresh(inv)
    return {"status": "200", "mensaje": "Inventario actualizado", "data": _serialize(inv)}

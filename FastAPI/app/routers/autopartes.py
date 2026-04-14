from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.data.db import get_db
from app.data.orm import Autoparte, Inventario, Categoria
from app.models.autopartes import AutoparteCreate, AutoparteUpdate
from app.security.auth import verify_api_key

router = APIRouter(prefix="/v1/autopartes", tags=["Autopartes"])


def _serialize(a: Autoparte) -> dict:
    inv = a.inventario
    stock = inv.stock_actual if inv else 0
    necesita = (inv.stock_actual <= inv.stock_minimo) if inv else False
    return {
        "id": a.id,
        "nombre": a.nombre,
        "descripcion": a.descripcion,
        "categoria_id": a.categoria_id,
        "categoria": {"id": a.categoria.id, "nombre": a.categoria.nombre} if a.categoria else None,
        "marca": a.marca,
        "precio": float(a.precio),
        "activo": a.activo,
        "stock_disponible": stock,
        "inventario": {
            "id": inv.id,
            "stock_actual": inv.stock_actual,
            "stock_minimo": inv.stock_minimo,
            "necesita_reposicion": necesita,
            "fecha_actualizacion": inv.fecha_actualizacion.isoformat() if inv.fecha_actualizacion else None,
        } if inv else None,
    }


@router.get("/")
async def listar_autopartes(
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
    search: Optional[str] = Query(None),
    categoria_id: Optional[int] = Query(None),
    solo_activos: bool = Query(True),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
):
    q = db.query(Autoparte)
    if solo_activos:
        q = q.filter(Autoparte.activo == True)
    if search:
        q = q.filter(
            Autoparte.nombre.ilike(f"%{search}%") | Autoparte.marca.ilike(f"%{search}%")
        )
    if categoria_id:
        q = q.filter(Autoparte.categoria_id == categoria_id)

    total = q.count()
    items = q.order_by(Autoparte.nombre).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "status": "200",
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": max(1, (total + per_page - 1) // per_page),
        "data": [_serialize(a) for a in items],
    }


@router.get("/buscar")
async def buscar_autopartes(
    q: str = Query(""),
    db: Session = Depends(get_db),
    _: str = Depends(verify_api_key),
):
    """Búsqueda rápida para autocomplete"""
    items = (
        db.query(Autoparte)
        .filter(
            Autoparte.activo == True,
            Autoparte.nombre.ilike(f"%{q}%") | Autoparte.marca.ilike(f"%{q}%"),
        )
        .limit(10)
        .all()
    )
    return {"status": "200", "data": [_serialize(a) for a in items]}


@router.get("/{id}")
async def obtener_autoparte(id: int, db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    a = db.query(Autoparte).filter(Autoparte.id == id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")
    return {"status": "200", "data": _serialize(a)}


@router.post("/")
async def crear_autoparte(payload: AutoparteCreate, db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    if not db.query(Categoria).filter(Categoria.id == payload.categoria_id).first():
        raise HTTPException(status_code=400, detail="Categoría no encontrada")
    a = Autoparte(
        nombre=payload.nombre,
        descripcion=payload.descripcion,
        categoria_id=payload.categoria_id,
        marca=payload.marca,
        precio=payload.precio,
        activo=payload.activo,
    )
    db.add(a)
    db.flush()
    inv = Inventario(
        autoparte_id=a.id,
        stock_actual=payload.stock_inicial,
        stock_minimo=payload.stock_minimo,
    )
    db.add(inv)
    db.commit()
    db.refresh(a)
    return {"status": "201", "mensaje": "Autoparte creada", "data": _serialize(a)}


@router.put("/{id}")
async def actualizar_autoparte(
    id: int, payload: AutoparteUpdate, db: Session = Depends(get_db), _: str = Depends(verify_api_key)
):
    a = db.query(Autoparte).filter(Autoparte.id == id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")
    if payload.nombre is not None:
        a.nombre = payload.nombre
    if payload.descripcion is not None:
        a.descripcion = payload.descripcion
    if payload.categoria_id is not None:
        a.categoria_id = payload.categoria_id
    if payload.marca is not None:
        a.marca = payload.marca
    if payload.precio is not None:
        a.precio = payload.precio
    if payload.activo is not None:
        a.activo = payload.activo
    db.commit()
    db.refresh(a)
    return {"status": "200", "mensaje": "Autoparte actualizada", "data": _serialize(a)}


@router.delete("/{id}")
async def desactivar_autoparte(id: int, db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    a = db.query(Autoparte).filter(Autoparte.id == id).first()
    if not a:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")
    a.activo = False
    db.commit()
    return {"status": "200", "mensaje": f"Autoparte {a.nombre} desactivada"}

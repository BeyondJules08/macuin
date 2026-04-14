from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.orm import Categoria
from app.models.autopartes import CategoriaCreate
from app.security.auth import verify_api_key

router = APIRouter(prefix="/v1/categorias", tags=["Categorías"])


def _serialize(c: Categoria) -> dict:
    return {"id": c.id, "nombre": c.nombre, "descripcion": c.descripcion}


@router.get("/")
async def listar_categorias(db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    cats = db.query(Categoria).order_by(Categoria.nombre).all()
    return {"status": "200", "total": len(cats), "data": [_serialize(c) for c in cats]}


@router.get("/{id}")
async def obtener_categoria(id: int, db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    c = db.query(Categoria).filter(Categoria.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return {"status": "200", "data": _serialize(c)}


@router.post("/")
async def crear_categoria(payload: CategoriaCreate, db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    if db.query(Categoria).filter(Categoria.nombre == payload.nombre).first():
        raise HTTPException(status_code=400, detail="La categoría ya existe")
    c = Categoria(nombre=payload.nombre, descripcion=payload.descripcion)
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"status": "201", "mensaje": "Categoría creada", "data": _serialize(c)}


@router.put("/{id}")
async def actualizar_categoria(
    id: int, payload: CategoriaCreate, db: Session = Depends(get_db), _: str = Depends(verify_api_key)
):
    c = db.query(Categoria).filter(Categoria.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    c.nombre = payload.nombre
    c.descripcion = payload.descripcion
    db.commit()
    db.refresh(c)
    return {"status": "200", "mensaje": "Categoría actualizada", "data": _serialize(c)}


@router.delete("/{id}")
async def eliminar_categoria(id: int, db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    c = db.query(Categoria).filter(Categoria.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(c)
    db.commit()
    return {"status": "200", "mensaje": f"Categoría {c.nombre} eliminada"}

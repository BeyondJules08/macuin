from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.orm import Role
from app.security.auth import verify_api_key

router = APIRouter(prefix="/v1/roles", tags=["Roles"])


@router.get("/")
async def listar_roles(db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    roles = db.query(Role).all()
    return {
        "status": "200",
        "total": len(roles),
        "data": [{"id": r.id, "nombre": r.nombre, "descripcion": r.descripcion} for r in roles],
    }


@router.get("/{id}")
async def obtener_rol(id: int, db: Session = Depends(get_db), _: str = Depends(verify_api_key)):
    rol = db.query(Role).filter(Role.id == id).first()
    if not rol:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return {"status": "200", "data": {"id": rol.id, "nombre": rol.nombre, "descripcion": rol.descripcion}}

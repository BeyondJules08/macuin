from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.orm import Cliente
from app.models.clientes import ClienteCreate, ClienteUpdate
from app.security.auth import get_current_subject, hash_password

router = APIRouter(prefix="/v1/clientes", tags=["Clientes Externos"])


def _serialize(c: Cliente) -> dict:
    return {
        "id": c.id,
        "nombre": c.nombre,
        "email": c.email,
        "telefono": c.telefono,
        "direccion": c.direccion,
        "fecha_registro": c.fecha_registro.isoformat() if c.fecha_registro else None,
        "activo": c.activo,
    }


@router.post("/registro")
async def registrar_cliente(payload: ClienteCreate, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    """Registro público de clientes externos (desde Laravel)"""
    if db.query(Cliente).filter(Cliente.email == payload.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    c = Cliente(
        nombre=payload.nombre,
        email=payload.email,
        password_hash=hash_password(payload.password),
        telefono=payload.telefono,
        direccion=payload.direccion,
        activo=True,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"status": "201", "mensaje": "Cliente registrado exitosamente", "data": _serialize(c)}


@router.get("/")
async def listar_clientes(db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    clientes = db.query(Cliente).order_by(Cliente.nombre).all()
    return {"status": "200", "total": len(clientes), "data": [_serialize(c) for c in clientes]}


@router.get("/{id}")
async def obtener_cliente(id: int, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    c = db.query(Cliente).filter(Cliente.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return {"status": "200", "data": _serialize(c)}


@router.put("/{id}")
async def actualizar_cliente(
    id: int, payload: ClienteUpdate, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)
):
    c = db.query(Cliente).filter(Cliente.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if payload.nombre is not None:
        c.nombre = payload.nombre
    if payload.email is not None:
        c.email = payload.email
    if payload.password is not None:
        c.password_hash = hash_password(payload.password)
    if payload.telefono is not None:
        c.telefono = payload.telefono
    if payload.direccion is not None:
        c.direccion = payload.direccion
    if payload.activo is not None:
        c.activo = payload.activo
    db.commit()
    db.refresh(c)
    return {"status": "200", "mensaje": "Cliente actualizado", "data": _serialize(c)}


@router.delete("/{id}")
async def eliminar_cliente(id: int, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    c = db.query(Cliente).filter(Cliente.id == id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    db.delete(c)
    db.commit()
    return {"status": "200", "mensaje": f"Cliente {c.nombre} eliminado"}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.data.db import get_db
from app.data.orm import Usuario, Role
from app.models.usuarios import UsuarioCreate, UsuarioUpdate
from app.security.auth import get_current_subject, hash_password

router = APIRouter(prefix="/v1/usuarios", tags=["Usuarios Internos"])


def _serialize(u: Usuario) -> dict:
    return {
        "id": u.id,
        "nombre": u.nombre,
        "email": u.email,
        "rol_id": u.rol_id,
        "rol": {"id": u.rol.id, "nombre": u.rol.nombre} if u.rol else None,
        "fecha_registro": u.fecha_registro.isoformat() if u.fecha_registro else None,
        "activo": u.activo,
    }


@router.get("/")
async def listar_usuarios(db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    usuarios = db.query(Usuario).order_by(Usuario.nombre).all()
    return {"status": "200", "total": len(usuarios), "data": [_serialize(u) for u in usuarios]}


@router.get("/{id}")
async def obtener_usuario(id: int, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    u = db.query(Usuario).filter(Usuario.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"status": "200", "data": _serialize(u)}


@router.post("/")
async def crear_usuario(payload: UsuarioCreate, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    if db.query(Usuario).filter(Usuario.email == payload.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    if not db.query(Role).filter(Role.id == payload.rol_id).first():
        raise HTTPException(status_code=400, detail="Rol no encontrado")
    u = Usuario(
        nombre=payload.nombre,
        email=payload.email,
        password_hash=hash_password(payload.password),
        rol_id=payload.rol_id,
        activo=payload.activo,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return {"status": "201", "mensaje": "Usuario creado", "data": _serialize(u)}


@router.put("/{id}")
async def actualizar_usuario(
    id: int, payload: UsuarioUpdate, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)
):
    u = db.query(Usuario).filter(Usuario.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if payload.nombre is not None:
        u.nombre = payload.nombre
    if payload.email is not None:
        existing = db.query(Usuario).filter(Usuario.email == payload.email, Usuario.id != id).first()
        if existing:
            raise HTTPException(status_code=400, detail="El email ya está en uso")
        u.email = payload.email
    if payload.password is not None:
        u.password_hash = hash_password(payload.password)
    if payload.rol_id is not None:
        u.rol_id = payload.rol_id
    if payload.activo is not None:
        u.activo = payload.activo
    db.commit()
    db.refresh(u)
    return {"status": "200", "mensaje": "Usuario actualizado", "data": _serialize(u)}


@router.delete("/{id}")
async def eliminar_usuario(id: int, db: Session = Depends(get_db), _claims: dict = Depends(get_current_subject)):
    u = db.query(Usuario).filter(Usuario.id == id).first()
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(u)
    db.commit()
    return {"status": "200", "mensaje": f"Usuario {u.nombre} eliminado"}

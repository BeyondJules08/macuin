"""OAuth2 + JWT security utilities for MACUIN FastAPI."""
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
import os

# ── Configuration ─────────────────────────────────────────────────────

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "macuin_jwt_super_secret_key_change_in_prod_2024")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme – the token URL points to the internal login endpoints
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/login", auto_error=False)
oauth2_scheme_cliente = OAuth2PasswordBearer(tokenUrl="v1/auth/login-cliente", auto_error=False)


# ── Password helpers ──────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT token creation ────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ── JWT token verification / dependency injection ────────────────────

def _decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_usuario(token: str = Depends(oauth2_scheme)) -> dict:
    """Extract and validate JWT for internal users (Flask)."""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = _decode_token(token)
    # Validate that this is a user token (not a client token)
    if payload.get("tipo") != "usuario":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token no corresponde a un usuario interno",
        )
    return payload


def get_current_cliente(token: str = Depends(oauth2_scheme_cliente)) -> dict:
    """Extract and validate JWT for external clients (Laravel)."""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = _decode_token(token)
    if payload.get("tipo") != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token no corresponde a un cliente externo",
        )
    return payload


def get_current_subject(token: str = Depends(oauth2_scheme)) -> dict:
    """Generic token validator – accepts either user or client token."""
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _decode_token(token)

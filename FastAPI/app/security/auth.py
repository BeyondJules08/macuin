"""OAuth2 + JWT security utilities for MACUIN FastAPI."""
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel

# ── Configuration ─────────────────────────────────────────────────────

SECRET_KEY = "b29fb2689f12fc2ce6cb71418df9827766cd1a10a251b820b603a24d1f430373"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
DUMMY_HASH = password_hash.hash("585426")

bearer_scheme = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# ── Pydantic models ───────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str


# ── Password helpers ──────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return password_hash.verify(plain, hashed)


# ── Simple credential authentication ─────────────────────────────────

def authenticate_user(username: str, password: str):
    userAuth = secrets.compare_digest(username, "Julian")
    passAuth = secrets.compare_digest(password, "585426")
    if not (userAuth and passAuth):
        return False
    return User(username=username)


# ── JWT token creation ────────────────────────────────────────────────

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ── JWT token verification / dependency injection ────────────────────

def _decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )


def _extract_token(credentials: Optional[HTTPAuthorizationCredentials]) -> str:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acceso no proporcionado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


def get_current_usuario(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> dict:
    """Extract and validate JWT for internal users (Flask)."""
    payload = _decode_token(_extract_token(credentials))
    if payload.get("tipo") != "usuario":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token no corresponde a un usuario interno",
        )
    return payload


def get_current_cliente(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> dict:
    """Extract and validate JWT for external clients (Laravel)."""
    payload = _decode_token(_extract_token(credentials))
    if payload.get("tipo") != "cliente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token no corresponde a un cliente externo",
        )
    return payload


def get_current_subject(credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme)) -> dict:
    """Generic token validator – accepts either user or client token."""
    return _decode_token(_extract_token(credentials))

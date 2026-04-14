"""Cliente HTTP para comunicarse con el FastAPI de MACUIN (OAuth2 + JWT)"""
import os
import requests
from datetime import datetime
from types import SimpleNamespace

API_URL = os.getenv("API_URL", "http://fastapi:8080")
API_USER = os.getenv("API_USER", "admin@macuin.com")       # internal user email
API_PASSWORD = os.getenv("API_PASSWORD", "admin123")       # internal user password

# Token state (module-level, shared across requests)
_access_token: str | None = None

_DATE_KEYS = {"fecha_pedido", "fecha_registro", "fecha_actualizacion", "fecha"}


# ── Token management ──────────────────────────────────────────────────

def _get_token() -> str:
    """Obtain (or refresh) the JWT token by logging in with API credentials."""
    global _access_token
    if _access_token:
        return _access_token

    r = requests.post(
        f"{API_URL}/v1/auth/login",
        headers={"Content-Type": "application/json"},
        json={"email": API_USER, "password": API_PASSWORD},
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    _access_token = data["data"]["access_token"]
    return _access_token


def _auth_headers() -> dict:
    return {"Authorization": f"Bearer {_get_token()}", "Content-Type": "application/json"}


def invalidate_token():
    """Force re-authentication on next request (e.g. after 401)."""
    global _access_token
    _access_token = None


# ── Conversión dict → objeto ────────────────────────────────────────

def to_obj(data):
    """Convierte recursivamente dicts/listas en SimpleNamespace para que los
    templates Jinja2 puedan acceder con notación punto (obj.campo)."""
    if isinstance(data, dict):
        converted = {}
        for k, v in data.items():
            if isinstance(v, str) and k in _DATE_KEYS:
                try:
                    v = datetime.fromisoformat(v.rstrip("Z"))
                except ValueError:
                    pass
            converted[k] = to_obj(v)
        return SimpleNamespace(**converted)
    if isinstance(data, list):
        return [to_obj(i) for i in data]
    return data


class Pagination:
    """Imita la paginación de Flask-SQLAlchemy para los templates existentes."""

    def __init__(self, items, page, per_page, total):
        self.items = items
        self.page = page
        self.per_page = per_page
        self.total = total
        self.pages = max(1, (total + per_page - 1) // per_page) if total else 1
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1
        self.next_num = page + 1

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (self.page - left_current - 1 < num < self.page + right_current)
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


# ── Métodos HTTP con auto-retry on 401 ───────────────────────────────

def _retry_on_401(fn, *args, **kwargs):
    """Execute an HTTP call; if 401, invalidate token and retry once."""
    try:
        return fn(*args, **kwargs)
    except requests.HTTPError as e:
        if e.response is not None and e.response.status_code == 401:
            invalidate_token()
            return fn(*args, **kwargs)
        raise


def _get(path, params=None):
    def _do():
        r = requests.get(f"{API_URL}{path}", headers=_auth_headers(), params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    return _retry_on_401(_do)


def _post(path, data):
    def _do():
        r = requests.post(f"{API_URL}{path}", headers=_auth_headers(), json=data, timeout=10)
        r.raise_for_status()
        return r.json()
    return _retry_on_401(_do)


def _put(path, data):
    def _do():
        r = requests.put(f"{API_URL}{path}", headers=_auth_headers(), json=data, timeout=10)
        r.raise_for_status()
        return r.json()
    return _retry_on_401(_do)


def _delete(path):
    def _do():
        r = requests.delete(f"{API_URL}{path}", headers=_auth_headers(), timeout=10)
        r.raise_for_status()
        return r.json()
    return _retry_on_401(_do)


def _stream(path, params=None):
    """Retorna el objeto response sin parsear (para descargas binarias)."""
    def _do():
        r = requests.get(f"{API_URL}{path}", headers=_auth_headers(), params=params, stream=True, timeout=30)
        r.raise_for_status()
        return r
    return _retry_on_401(_do)


# ── Auth ────────────────────────────────────────────────────────────

def login_usuario(email, password):
    """Login for Flask user session – returns user data + token."""
    try:
        r = requests.post(
            f"{API_URL}/v1/auth/login",
            headers={"Content-Type": "application/json"},
            json={"email": email, "password": password},
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


# ── Usuarios ────────────────────────────────────────────────────────

def get_usuarios():
    data = _get("/v1/usuarios/")
    return [to_obj(u) for u in data["data"]]


def get_usuario(id):
    data = _get(f"/v1/usuarios/{id}")
    return to_obj(data["data"])


def create_usuario(payload):
    return _post("/v1/usuarios/", payload)


def update_usuario(id, payload):
    return _put(f"/v1/usuarios/{id}", payload)


def delete_usuario(id):
    return _delete(f"/v1/usuarios/{id}")


def get_roles():
    data = _get("/v1/roles/")
    return [to_obj(r) for r in data["data"]]


# ── Categorías ──────────────────────────────────────────────────────

def get_categorias():
    data = _get("/v1/categorias/")
    return [to_obj(c) for c in data["data"]]


# ── Autopartes ──────────────────────────────────────────────────────

def get_autopartes(page=1, per_page=20, search="", categoria_id=None):
    params = {"page": page, "per_page": per_page}
    if search:
        params["search"] = search
    if categoria_id:
        params["categoria_id"] = categoria_id
    data = _get("/v1/autopartes/", params)
    items = [to_obj(a) for a in data["data"]]
    return Pagination(items, data["page"], data["per_page"], data["total"])


def get_autoparte(id):
    data = _get(f"/v1/autopartes/{id}")
    return to_obj(data["data"])


def get_autopartes_activas():
    data = _get("/v1/autopartes/", {"solo_activos": True, "per_page": 200})
    return [to_obj(a) for a in data["data"]]


def search_autopartes(q):
    data = _get("/v1/autopartes/buscar", {"q": q})
    return data["data"]


def create_autoparte(payload):
    return _post("/v1/autopartes/", payload)


def update_autoparte(id, payload):
    return _put(f"/v1/autopartes/{id}", payload)


def delete_autoparte(id):
    return _delete(f"/v1/autopartes/{id}")


# ── Inventario ──────────────────────────────────────────────────────

def get_inventario(page=1, per_page=20, search="", bajo_stock=False):
    params = {"page": page, "per_page": per_page}
    if search:
        params["search"] = search
    if bajo_stock:
        params["bajo_stock"] = True
    data = _get("/v1/inventario/", params)
    items = [to_obj(i) for i in data["data"]]
    return Pagination(items, data["page"], data["per_page"], data["total"])


def get_inventario_item(id):
    data = _get(f"/v1/inventario/{id}")
    return to_obj(data["data"])


def update_inventario(id, payload):
    return _put(f"/v1/inventario/{id}", payload)


def get_bajo_stock():
    data = _get("/v1/inventario/", {"bajo_stock": True, "per_page": 100})
    return [to_obj(i) for i in data["data"]]


# ── Pedidos ─────────────────────────────────────────────────────────

def get_pedidos(page=1, per_page=20, estado_id=None, usuario_id=None):
    params = {"page": page, "per_page": per_page}
    if estado_id:
        params["estado_id"] = estado_id
    if usuario_id:
        params["usuario_id"] = usuario_id
    data = _get("/v1/pedidos/", params)
    items = [to_obj(p) for p in data["data"]]
    return Pagination(items, data["page"], data["per_page"], data["total"])


def get_pedido(id):
    data = _get(f"/v1/pedidos/{id}")
    return to_obj(data["data"])


def create_pedido(usuario_id, items):
    return _post("/v1/pedidos/", {"usuario_id": usuario_id, "items": items})


def cambiar_estado_pedido(id, estado_id):
    return _put(f"/v1/pedidos/{id}/estado", {"estado_id": estado_id})


def get_estados_pedido():
    data = _get("/v1/pedidos/estados/")
    return [to_obj(e) for e in data["data"]]


# ── Dashboard stats ─────────────────────────────────────────────────

def get_dashboard_stats():
    try:
        autopartes_data = _get("/v1/autopartes/", {"per_page": 1})
        pedidos_data = _get("/v1/pedidos/", {"per_page": 1})
        pendientes = _get("/v1/pedidos/", {"per_page": 1, "estado_id": _get_estado_id("Pendiente")})
        bajo_stock = _get("/v1/inventario/", {"bajo_stock": True, "per_page": 5})
        recientes = _get("/v1/pedidos/", {"per_page": 5})

        from datetime import datetime
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        todos_pedidos = _get("/v1/pedidos/", {"per_page": 1000})
        ventas_mes = sum(
            float(p["total"])
            for p in todos_pedidos.get("data", [])
            if p.get("fecha_pedido")
            and datetime.fromisoformat(p["fecha_pedido"].rstrip("Z")) >= inicio_mes
        )

        return {
            "total_autopartes": autopartes_data["total"],
            "total_pedidos": pedidos_data["total"],
            "pedidos_pendientes": pendientes["total"],
            "bajo_stock_items": [to_obj(i) for i in bajo_stock.get("data", [])[:5]],
            "pedidos_recientes": [to_obj(p) for p in recientes.get("data", [])[:5]],
            "ventas_mes": ventas_mes,
        }
    except Exception:
        return {
            "total_autopartes": 0, "total_pedidos": 0, "pedidos_pendientes": 0,
            "bajo_stock_items": [], "pedidos_recientes": [], "ventas_mes": 0,
        }


def _get_estado_id(nombre):
    try:
        estados = _get("/v1/pedidos/estados/")
        for e in estados.get("data", []):
            if e.get("nombre") == nombre:
                return e["id"]
    except Exception:
        pass
    return None

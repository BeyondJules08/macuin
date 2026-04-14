from fastapi import FastAPI
from app.data.db import engine
from app.data import orm
from app.routers import auth, roles, usuarios, clientes, autopartes, categorias, inventario, pedidos, reportes

# Crear tablas
orm.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MACUIN API",
    description="API central del sistema de gestión de autopartes MACUIN. "
                "Único punto de acceso a la base de datos para Flask y Laravel.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(usuarios.router)
app.include_router(clientes.router)
app.include_router(autopartes.router)
app.include_router(categorias.router)
app.include_router(inventario.router)
app.include_router(pedidos.router)
app.include_router(reportes.router)


@app.get("/", tags=["Info"])
async def root():
    return {"mensaje": "MACUIN API funcionando", "version": "1.0.0", "docs": "/docs"}


@app.get("/health", tags=["Info"])
async def health():
    return {"status": "ok"}

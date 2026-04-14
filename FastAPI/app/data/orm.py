from sqlalchemy import Column, Integer, String, Boolean, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .db import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(String(150))

    usuarios = relationship("Usuario", back_populates="rol")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    rol_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    rol = relationship("Role", back_populates="usuarios")
    pedidos = relationship("Pedido", back_populates="usuario")


class Categoria(Base):
    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, unique=True)
    descripcion = Column(String(150))

    autopartes = relationship("Autoparte", back_populates="categoria")


class Autoparte(Base):
    __tablename__ = "autopartes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(150), nullable=False)
    descripcion = Column(Text)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    marca = Column(String(100))
    precio = Column(Numeric(10, 2), nullable=False)
    activo = Column(Boolean, default=True)

    categoria = relationship("Categoria", back_populates="autopartes")
    inventario = relationship("Inventario", back_populates="autoparte", uselist=False)
    detalles_pedido = relationship("DetallePedido", back_populates="autoparte")
    detalles_externo = relationship("DetallePedidoExterno", back_populates="autoparte")


class Inventario(Base):
    __tablename__ = "inventarios"

    id = Column(Integer, primary_key=True, index=True)
    autoparte_id = Column(Integer, ForeignKey("autopartes.id"), nullable=False, unique=True)
    stock_actual = Column(Integer, nullable=False, default=0)
    stock_minimo = Column(Integer, nullable=False, default=0)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    autoparte = relationship("Autoparte", back_populates="inventario")


class EstadoPedido(Base):
    __tablename__ = "estados_pedido"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False, unique=True)

    pedidos = relationship("Pedido", back_populates="estado")
    pedidos_externos = relationship("PedidoExterno", back_populates="estado")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados_pedido.id"), nullable=False)
    fecha_pedido = Column(DateTime, default=datetime.utcnow)
    total = Column(Numeric(10, 2), nullable=False, default=0.00)

    usuario = relationship("Usuario", back_populates="pedidos")
    estado = relationship("EstadoPedido", back_populates="pedidos")
    detalles = relationship("DetallePedido", back_populates="pedido", cascade="all, delete-orphan")


class DetallePedido(Base):
    __tablename__ = "detalle_pedido"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    autoparte_id = Column(Integer, ForeignKey("autopartes.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)

    pedido = relationship("Pedido", back_populates="detalles")
    autoparte = relationship("Autoparte", back_populates="detalles_pedido")


class Cliente(Base):
    """Usuarios externos registrados desde Laravel"""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    password_hash = Column(String(255), nullable=False)
    telefono = Column(String(20))
    direccion = Column(String(200))
    fecha_registro = Column(DateTime, default=datetime.utcnow)
    activo = Column(Boolean, default=True)

    pedidos_externos = relationship("PedidoExterno", back_populates="cliente")


class PedidoExterno(Base):
    """Pedidos realizados por clientes externos (desde Laravel)"""
    __tablename__ = "pedidos_externos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    estado_id = Column(Integer, ForeignKey("estados_pedido.id"), nullable=False)
    fecha_pedido = Column(DateTime, default=datetime.utcnow)
    total = Column(Numeric(10, 2), nullable=False, default=0.00)
    notas = Column(Text)

    cliente = relationship("Cliente", back_populates="pedidos_externos")
    estado = relationship("EstadoPedido", back_populates="pedidos_externos")
    detalles = relationship(
        "DetallePedidoExterno", back_populates="pedido_externo", cascade="all, delete-orphan"
    )


class DetallePedidoExterno(Base):
    __tablename__ = "detalle_pedido_externo"

    id = Column(Integer, primary_key=True, index=True)
    pedido_externo_id = Column(Integer, ForeignKey("pedidos_externos.id"), nullable=False)
    autoparte_id = Column(Integer, ForeignKey("autopartes.id"), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)

    pedido_externo = relationship("PedidoExterno", back_populates="detalles")
    autoparte = relationship("Autoparte", back_populates="detalles_externo")

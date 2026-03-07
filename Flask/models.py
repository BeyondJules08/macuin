from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Role(db.Model):
    """Modelo para roles de usuario"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    descripcion = db.Column(db.String(150))
    
    # Relaciones
    usuarios = db.relationship('Usuario', backref='rol', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.nombre}>'

class Usuario(UserMixin, db.Model):
    """Modelo para usuarios del sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    pedidos = db.relationship('Pedido', backref='usuario', lazy='dynamic')
    
    def set_password(self, password):
        """Establece el hash de la contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<Usuario {self.email}>'

class Categoria(db.Model):
    """Modelo para categorías de autopartes"""
    __tablename__ = 'categorias'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    descripcion = db.Column(db.String(150))
    
    # Relaciones
    autopartes = db.relationship('Autoparte', backref='categoria', lazy='dynamic')
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'

class Autoparte(db.Model):
    """Modelo para autopartes"""
    __tablename__ = 'autopartes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    marca = db.Column(db.String(100))
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    
    # Relaciones
    inventario = db.relationship('Inventario', backref='autoparte', uselist=False, cascade='all, delete-orphan')
    detalles_pedido = db.relationship('DetallePedido', backref='autoparte', lazy='dynamic')
    
    def __repr__(self):
        return f'<Autoparte {self.nombre}>'
    
    @property
    def stock_disponible(self):
        """Retorna el stock disponible de esta autoparte"""
        if self.inventario:
            return self.inventario.stock_actual
        return 0

class Inventario(db.Model):
    """Modelo para inventario de autopartes"""
    __tablename__ = 'inventarios'
    
    id = db.Column(db.Integer, primary_key=True)
    autoparte_id = db.Column(db.Integer, db.ForeignKey('autopartes.id'), nullable=False, unique=True)
    stock_actual = db.Column(db.Integer, nullable=False, default=0)
    stock_minimo = db.Column(db.Integer, nullable=False, default=0)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Inventario autoparte_id={self.autoparte_id} stock={self.stock_actual}>'
    
    @property
    def necesita_reposicion(self):
        """Indica si el stock está por debajo del mínimo"""
        return self.stock_actual <= self.stock_minimo
    
    @property
    def porcentaje_stock(self):
        """Calcula el porcentaje de stock respecto al mínimo"""
        if self.stock_minimo == 0:
            return 100
        return (self.stock_actual / self.stock_minimo) * 100

class EstadoPedido(db.Model):
    """Modelo para estados de pedidos"""
    __tablename__ = 'estados_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
    
    # Relaciones
    pedidos = db.relationship('Pedido', backref='estado', lazy='dynamic')
    
    def __repr__(self):
        return f'<EstadoPedido {self.nombre}>'

class Pedido(db.Model):
    """Modelo para pedidos"""
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    estado_id = db.Column(db.Integer, db.ForeignKey('estados_pedido.id'), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    
    # Relaciones
    detalles = db.relationship('DetallePedido', backref='pedido', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Pedido {self.id} - Total: ${self.total}>'
    
    def calcular_total(self):
        """Calcula el total del pedido basado en sus detalles"""
        total = sum(detalle.cantidad * detalle.precio_unitario for detalle in self.detalles)
        self.total = total
        return total

class DetallePedido(db.Model):
    """Modelo para detalles de pedidos"""
    __tablename__ = 'detalle_pedido'
    
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    autoparte_id = db.Column(db.Integer, db.ForeignKey('autopartes.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    
    def __repr__(self):
        return f'<DetallePedido pedido_id={self.pedido_id} autoparte_id={self.autoparte_id}>'
    
    @property
    def subtotal(self):
        """Calcula el subtotal de este detalle"""
        return self.cantidad * self.precio_unitario

import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
from config import config
from models import db, Usuario, Role, Autoparte, Categoria, Inventario, Pedido, DetallePedido, EstadoPedido
from datetime import datetime
from sqlalchemy import func

def create_app(config_name=None):
    """Factory para crear la aplicación Flask"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Inicializar extensiones
    db.init_app(app)
    
    # Configurar Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Por favor inicia sesión para acceder a esta página.'
    login_manager.login_message_category = 'warning'
    
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    # Decorador para verificar roles
    def role_required(*role_names):
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                if not current_user.is_authenticated:
                    flash('Por favor inicia sesión.', 'warning')
                    return redirect(url_for('login'))
                if current_user.rol.nombre not in role_names and current_user.rol.nombre != 'Administrador':
                    flash('No tienes permisos para acceder a esta página.', 'danger')
                    return redirect(url_for('dashboard'))
                return f(*args, **kwargs)
            return decorated_function
        return decorator
    
    # Context processor para hacer disponibles variables en todas las plantillas
    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)
    
    # ==================== RUTAS DE AUTENTICACIÓN ====================
    
    @app.route('/')
    def index():
        """Página de inicio - redirige al dashboard si está autenticado"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Ruta de inicio de sesión"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            remember = request.form.get('remember', False)
            
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario and usuario.check_password(password):
                if not usuario.activo:
                    flash('Tu cuenta está inactiva. Contacta al administrador.', 'danger')
                    return render_template('login.html')
                
                login_user(usuario, remember=remember)
                flash(f'Bienvenido {usuario.nombre}!', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Email o contraseña incorrectos.', 'danger')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Ruta de cierre de sesión"""
        logout_user()
        flash('Has cerrado sesión exitosamente.', 'info')
        return redirect(url_for('login'))
    
    # ==================== DASHBOARD ====================
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard principal del sistema"""
        # Estadísticas generales
        total_autopartes = Autoparte.query.filter_by(activo=True).count()
        total_pedidos = Pedido.query.count()
        pedidos_pendientes = Pedido.query.join(EstadoPedido).filter(
            EstadoPedido.nombre.in_(['Pendiente', 'En Proceso'])
        ).count()
        
        # Productos con stock bajo
        productos_bajo_stock = db.session.query(Autoparte, Inventario).join(
            Inventario, Autoparte.id == Inventario.autoparte_id
        ).filter(
            Inventario.stock_actual <= Inventario.stock_minimo
        ).limit(5).all()
        
        # Pedidos recientes
        pedidos_recientes = Pedido.query.order_by(Pedido.fecha_pedido.desc()).limit(5).all()
        
        # Ventas totales del mes actual
        inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        ventas_mes = db.session.query(func.sum(Pedido.total)).filter(
            Pedido.fecha_pedido >= inicio_mes
        ).scalar() or 0
        
        return render_template('dashboard.html',
                             total_autopartes=total_autopartes,
                             total_pedidos=total_pedidos,
                             pedidos_pendientes=pedidos_pendientes,
                             productos_bajo_stock=productos_bajo_stock,
                             pedidos_recientes=pedidos_recientes,
                             ventas_mes=ventas_mes)
    
    # ==================== RUTAS DE AUTOPARTES ====================
    
    @app.route('/autopartes')
    @login_required
    def autopartes_list():
        """Lista de autopartes"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        categoria_id = request.args.get('categoria', type=int)
        
        query = Autoparte.query
        
        if search:
            query = query.filter(
                db.or_(
                    Autoparte.nombre.contains(search),
                    Autoparte.marca.contains(search)
                )
            )
        
        if categoria_id:
            query = query.filter_by(categoria_id=categoria_id)
        
        autopartes = query.order_by(Autoparte.nombre).paginate(
            page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
        )
        
        categorias = Categoria.query.order_by(Categoria.nombre).all()
        
        return render_template('autopartes/list.html',
                             autopartes=autopartes,
                             categorias=categorias,
                             search=search,
                             categoria_id=categoria_id)
    
    @app.route('/autopartes/crear', methods=['GET', 'POST'])
    @login_required
    @role_required('Administrador', 'Almacén')
    def autopartes_create():
        """Crear nueva autoparte"""
        if request.method == 'POST':
            nombre = request.form.get('nombre')
            descripcion = request.form.get('descripcion')
            categoria_id = request.form.get('categoria_id', type=int)
            marca = request.form.get('marca')
            precio = request.form.get('precio', type=float)
            stock_inicial = request.form.get('stock_inicial', 0, type=int)
            stock_minimo = request.form.get('stock_minimo', 0, type=int)
            
            try:
                # Crear autoparte
                autoparte = Autoparte(
                    nombre=nombre,
                    descripcion=descripcion,
                    categoria_id=categoria_id,
                    marca=marca,
                    precio=precio,
                    activo=True
                )
                db.session.add(autoparte)
                db.session.flush()
                
                # Crear inventario
                inventario = Inventario(
                    autoparte_id=autoparte.id,
                    stock_actual=stock_inicial,
                    stock_minimo=stock_minimo
                )
                db.session.add(inventario)
                
                db.session.commit()
                flash('Autoparte creada exitosamente.', 'success')
                return redirect(url_for('autopartes_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear autoparte: {str(e)}', 'danger')
        
        categorias = Categoria.query.order_by(Categoria.nombre).all()
        return render_template('autopartes/form.html', categorias=categorias)
    
    @app.route('/autopartes/<int:id>/editar', methods=['GET', 'POST'])
    @login_required
    @role_required('Administrador', 'Almacén')
    def autopartes_edit(id):
        """Editar autoparte"""
        autoparte = Autoparte.query.get_or_404(id)
        
        if request.method == 'POST':
            autoparte.nombre = request.form.get('nombre')
            autoparte.descripcion = request.form.get('descripcion')
            autoparte.categoria_id = request.form.get('categoria_id', type=int)
            autoparte.marca = request.form.get('marca')
            autoparte.precio = request.form.get('precio', type=float)
            autoparte.activo = request.form.get('activo') == 'on'
            
            try:
                db.session.commit()
                flash('Autoparte actualizada exitosamente.', 'success')
                return redirect(url_for('autopartes_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar autoparte: {str(e)}', 'danger')
        
        categorias = Categoria.query.order_by(Categoria.nombre).all()
        return render_template('autopartes/form.html', autoparte=autoparte, categorias=categorias)
    
    @app.route('/autopartes/<int:id>/eliminar', methods=['POST'])
    @login_required
    @role_required('Administrador')
    def autopartes_delete(id):
        """Eliminar (desactivar) autoparte"""
        autoparte = Autoparte.query.get_or_404(id)
        autoparte.activo = False
        
        try:
            db.session.commit()
            flash('Autoparte desactivada exitosamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al desactivar autoparte: {str(e)}', 'danger')
        
        return redirect(url_for('autopartes_list'))
    
    # ==================== RUTAS DE INVENTARIO ====================
    
    @app.route('/inventario')
    @login_required
    @role_required('Administrador', 'Almacén')
    def inventario_list():
        """Lista de inventario"""
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        bajo_stock = request.args.get('bajo_stock', type=bool)
        
        query = db.session.query(Autoparte, Inventario).join(
            Inventario, Autoparte.id == Inventario.autoparte_id
        ).filter(Autoparte.activo == True)
        
        if search:
            query = query.filter(
                db.or_(
                    Autoparte.nombre.contains(search),
                    Autoparte.marca.contains(search)
                )
            )
        
        if bajo_stock:
            query = query.filter(Inventario.stock_actual <= Inventario.stock_minimo)
        
        inventarios = query.order_by(Autoparte.nombre).paginate(
            page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
        )
        
        return render_template('inventario/list.html',
                             inventarios=inventarios,
                             search=search,
                             bajo_stock=bajo_stock)
    
    @app.route('/inventario/<int:id>/actualizar', methods=['GET', 'POST'])
    @login_required
    @role_required('Administrador', 'Almacén')
    def inventario_update(id):
        """Actualizar stock de inventario"""
        inventario = Inventario.query.get_or_404(id)
        
        if request.method == 'POST':
            operacion = request.form.get('operacion')
            cantidad = request.form.get('cantidad', 0, type=int)
            
            if operacion == 'agregar':
                inventario.stock_actual += cantidad
            elif operacion == 'restar':
                if inventario.stock_actual >= cantidad:
                    inventario.stock_actual -= cantidad
                else:
                    flash('No hay suficiente stock para restar.', 'danger')
                    return redirect(url_for('inventario_update', id=id))
            elif operacion == 'establecer':
                inventario.stock_actual = cantidad
            
            inventario.stock_minimo = request.form.get('stock_minimo', inventario.stock_minimo, type=int)
            
            try:
                db.session.commit()
                flash('Inventario actualizado exitosamente.', 'success')
                return redirect(url_for('inventario_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar inventario: {str(e)}', 'danger')
        
        return render_template('inventario/update.html', inventario=inventario)
    
    # ==================== RUTAS DE PEDIDOS ====================
    
    @app.route('/pedidos')
    @login_required
    def pedidos_list():
        """Lista de pedidos"""
        page = request.args.get('page', 1, type=int)
        estado_id = request.args.get('estado', type=int)
        
        query = Pedido.query
        
        # Filtro por rol
        if current_user.rol.nombre == 'Ventas':
            query = query.filter_by(usuario_id=current_user.id)
        
        if estado_id:
            query = query.filter_by(estado_id=estado_id)
        
        pedidos = query.order_by(Pedido.fecha_pedido.desc()).paginate(
            page=page, per_page=app.config['ITEMS_PER_PAGE'], error_out=False
        )
        
        estados = EstadoPedido.query.all()
        
        return render_template('pedidos/list.html',
                             pedidos=pedidos,
                             estados=estados,
                             estado_id=estado_id)
    
    @app.route('/pedidos/crear', methods=['GET', 'POST'])
    @login_required
    @role_required('Administrador', 'Ventas')
    def pedidos_create():
        """Crear nuevo pedido"""
        if request.method == 'POST':
            try:
                # Crear pedido
                estado_pendiente = EstadoPedido.query.filter_by(nombre='Pendiente').first()
                pedido = Pedido(
                    usuario_id=current_user.id,
                    estado_id=estado_pendiente.id,
                    total=0
                )
                db.session.add(pedido)
                db.session.flush()
                
                # Procesar detalles del pedido
                autopartes_ids = request.form.getlist('autoparte_id[]')
                cantidades = request.form.getlist('cantidad[]')
                
                for autoparte_id, cantidad in zip(autopartes_ids, cantidades):
                    if autoparte_id and cantidad:
                        autoparte = Autoparte.query.get(int(autoparte_id))
                        cantidad_int = int(cantidad)
                        
                        # Verificar stock
                        if autoparte.inventario and autoparte.inventario.stock_actual >= cantidad_int:
                            detalle = DetallePedido(
                                pedido_id=pedido.id,
                                autoparte_id=autoparte.id,
                                cantidad=cantidad_int,
                                precio_unitario=autoparte.precio
                            )
                            db.session.add(detalle)
                            
                            # Descontar del inventario
                            autoparte.inventario.stock_actual -= cantidad_int
                        else:
                            raise Exception(f'Stock insuficiente para {autoparte.nombre}')
                
                # Calcular total
                pedido.calcular_total()
                
                db.session.commit()
                flash('Pedido creado exitosamente.', 'success')
                return redirect(url_for('pedidos_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear pedido: {str(e)}', 'danger')
        
        autopartes = Autoparte.query.filter_by(activo=True).order_by(Autoparte.nombre).all()
        return render_template('pedidos/form.html', autopartes=autopartes)
    
    @app.route('/pedidos/<int:id>')
    @login_required
    def pedidos_detail(id):
        """Detalle de un pedido"""
        pedido = Pedido.query.get_or_404(id)
        
        # Verificar permisos
        if current_user.rol.nombre == 'Ventas' and pedido.usuario_id != current_user.id:
            flash('No tienes permisos para ver este pedido.', 'danger')
            return redirect(url_for('pedidos_list'))
        
        return render_template('pedidos/detail.html', pedido=pedido)
    
    @app.route('/pedidos/<int:id>/cambiar-estado', methods=['POST'])
    @login_required
    @role_required('Administrador', 'Logística')
    def pedidos_change_status(id):
        """Cambiar estado de un pedido"""
        pedido = Pedido.query.get_or_404(id)
        nuevo_estado_id = request.form.get('estado_id', type=int)
        
        pedido.estado_id = nuevo_estado_id
        
        try:
            db.session.commit()
            flash('Estado del pedido actualizado.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar estado: {str(e)}', 'danger')
        
        return redirect(url_for('pedidos_detail', id=id))
    
    # ==================== RUTAS DE USUARIOS (Solo Admin) ====================
    
    @app.route('/usuarios')
    @login_required
    @role_required('Administrador')
    def usuarios_list():
        """Lista de usuarios"""
        usuarios = Usuario.query.order_by(Usuario.nombre).all()
        return render_template('usuarios/list.html', usuarios=usuarios)
    
    @app.route('/usuarios/crear', methods=['GET', 'POST'])
    @login_required
    @role_required('Administrador')
    def usuarios_create():
        """Crear nuevo usuario"""
        if request.method == 'POST':
            nombre = request.form.get('nombre')
            email = request.form.get('email')
            password = request.form.get('password')
            rol_id = request.form.get('rol_id', type=int)
            
            # Verificar si el email ya existe
            if Usuario.query.filter_by(email=email).first():
                flash('El email ya está registrado.', 'danger')
                return redirect(url_for('usuarios_create'))
            
            try:
                usuario = Usuario(
                    nombre=nombre,
                    email=email,
                    rol_id=rol_id,
                    activo=True
                )
                usuario.set_password(password)
                
                db.session.add(usuario)
                db.session.commit()
                flash('Usuario creado exitosamente.', 'success')
                return redirect(url_for('usuarios_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al crear usuario: {str(e)}', 'danger')
        
        roles = Role.query.all()
        return render_template('usuarios/form.html', roles=roles)
    
    @app.route('/usuarios/<int:id>/editar', methods=['GET', 'POST'])
    @login_required
    @role_required('Administrador')
    def usuarios_edit(id):
        """Editar usuario"""
        usuario = Usuario.query.get_or_404(id)
        
        if request.method == 'POST':
            usuario.nombre = request.form.get('nombre')
            usuario.email = request.form.get('email')
            usuario.rol_id = request.form.get('rol_id', type=int)
            usuario.activo = request.form.get('activo') == 'on'
            
            # Actualizar contraseña solo si se proporciona una nueva
            new_password = request.form.get('password')
            if new_password:
                usuario.set_password(new_password)
            
            try:
                db.session.commit()
                flash('Usuario actualizado exitosamente.', 'success')
                return redirect(url_for('usuarios_list'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar usuario: {str(e)}', 'danger')
        
        roles = Role.query.all()
        return render_template('usuarios/form.html', usuario=usuario, roles=roles)
    
    # ==================== API ENDPOINTS ====================
    
    @app.route('/api/autopartes/buscar')
    @login_required
    def api_autopartes_search():
        """API para buscar autopartes (autocomplete)"""
        query = request.args.get('q', '')
        
        autopartes = Autoparte.query.filter(
            Autoparte.activo == True,
            db.or_(
                Autoparte.nombre.contains(query),
                Autoparte.marca.contains(query)
            )
        ).limit(10).all()
        
        return jsonify([{
            'id': a.id,
            'nombre': a.nombre,
            'marca': a.marca,
            'precio': float(a.precio),
            'stock': a.stock_disponible
        } for a in autopartes])
    
    @app.route('/api/estadisticas')
    @login_required
    def api_statistics():
        """API para obtener estadísticas del dashboard"""
        # Aquí puedes agregar más estadísticas según necesites
        return jsonify({
            'total_autopartes': Autoparte.query.filter_by(activo=True).count(),
            'total_pedidos': Pedido.query.count(),
            'bajo_stock': Inventario.query.filter(
                Inventario.stock_actual <= Inventario.stock_minimo
            ).count()
        })
    
    # ==================== MANEJO DE ERRORES ====================
    
    @app.errorhandler(404)
    def not_found(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Inicializar datos si es necesario
    if os.environ.get('INIT_MOCK_DATA') == 'true':
        with app.app_context():
            seed_data(db)
            
    return app

def seed_data(db):
    """Puebla la base de datos con datos iniciales para visualización"""
    print("Sembrando datos iniciales...")
    
    # Solo sembrar si la base de datos está vacía (o forzar limpieza si se desea)
    db.create_all()
    
    if Usuario.query.first():
        print("La base de datos ya contiene datos. Omitiendo siembra.")
        return

    # Roles
    roles = {
        'Administrador': Role(nombre='Administrador', descripcion='Acceso completo'),
        'Ventas': Role(nombre='Ventas', descripcion='Gestión de ventas'),
        'Almacén': Role(nombre='Almacén', descripcion='Gestión de stock'),
        'Logística': Role(nombre='Logística', descripcion='Gestión de envíos')
    }
    for r in roles.values(): db.session.add(r)
    db.session.commit()

    # Usuarios
    admin = Usuario(nombre='Admin Macuin', email='admin@macuin.com', rol_id=roles['Administrador'].id)
    admin.set_password('admin123')
    db.session.add(admin)
    
    ventas = Usuario(nombre='Juan Ventas', email='ventas@macuin.com', rol_id=roles['Ventas'].id)
    ventas.set_password('ventas123')
    db.session.add(ventas)
    
    db.session.commit()

    # Categorías
    cats = {
        'Motor': Categoria(nombre='Motor'),
        'Frenos': Categoria(nombre='Frenos'),
        'Suspensión': Categoria(nombre='Suspensión')
    }
    for c in cats.values(): db.session.add(c)
    db.session.commit()

    # Autopartes e Inventario
    parts_data = [
        ('Filtro Aceite', cats['Motor'].id, 150.0, 50, 10),
        ('Pastillas Freno', cats['Frenos'].id, 850.0, 30, 5),
        ('Amortiguador', cats['Suspensión'].id, 1200.0, 5, 10) # Bajo stock
    ]
    
    for name, cat_id, price, stock, min_stock in parts_data:
        p = Autoparte(nombre=name, categoria_id=cat_id, precio=price, activo=True)
        db.session.add(p)
        db.session.flush()
        inv = Inventario(autoparte_id=p.id, stock_actual=stock, stock_minimo=min_stock)
        db.session.add(inv)
    
    # Estados
    status_objs = {}
    estados = ['Pendiente', 'En Proceso', 'Entregado', 'Cancelado']
    for e in estados:
        obj = EstadoPedido(nombre=e)
        db.session.add(obj)
        status_objs[e] = obj
    db.session.commit()

    # Pedido de ejemplo
    p1 = Pedido(usuario_id=ventas.id, estado_id=status_objs['Pendiente'].id, total=300.0)
    db.session.add(p1)
    db.session.commit()
    
    dp1 = DetallePedido(pedido_id=p1.id, autoparte_id=1, cantidad=2, precio_unitario=150.0)
    db.session.add(dp1)
    db.session.commit()

    print("Datos sembrados exitosamente.")

# Crear la aplicación
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

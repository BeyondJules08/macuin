"""
Script para inicializar la base de datos SQLite con datos de prueba
Ejecutar: python init_db.py
"""

from app import create_app
from models import db, Role, Usuario, Categoria, Autoparte, Inventario, EstadoPedido, Pedido, DetallePedido
from datetime import datetime

def init_database():
    """Inicializa la base de datos con datos de prueba"""
    
    app = create_app()
    
    with app.app_context():
        # Eliminar tablas existentes y crear nuevas
        print("Eliminando tablas existentes...")
        db.drop_all()
        
        print("Creando tablas...")
        db.create_all()
        
        # ==================== ROLES ====================
        print("Creando roles...")
        roles_data = [
            {'nombre': 'Administrador', 'descripcion': 'Acceso completo al sistema'},
            {'nombre': 'Ventas', 'descripcion': 'Gestión de ventas y pedidos'},
            {'nombre': 'Almacén', 'descripcion': 'Gestión de inventario y stock'},
            {'nombre': 'Logística', 'descripcion': 'Gestión de envíos y distribución'}
        ]
        
        for rol_data in roles_data:
            rol = Role(**rol_data)
            db.session.add(rol)
        
        db.session.commit()
        print(f"   {len(roles_data)} roles creados")
        
        # ==================== USUARIOS ====================
        print("Creando usuarios...")
        
        # Obtener roles
        rol_admin = Role.query.filter_by(nombre='Administrador').first()
        rol_ventas = Role.query.filter_by(nombre='Ventas').first()
        rol_almacen = Role.query.filter_by(nombre='Almacén').first()
        rol_logistica = Role.query.filter_by(nombre='Logística').first()
        
        usuarios_data = [
            {'nombre': 'Administrador', 'email': 'admin@macuin.com', 'password': 'admin123', 'rol_id': rol_admin.id},
            {'nombre': 'Juan Pérez', 'email': 'ventas@macuin.com', 'password': 'ventas123', 'rol_id': rol_ventas.id},
            {'nombre': 'María García', 'email': 'almacen@macuin.com', 'password': 'almacen123', 'rol_id': rol_almacen.id},
            {'nombre': 'Carlos López', 'email': 'logistica@macuin.com', 'password': 'logistica123', 'rol_id': rol_logistica.id}
        ]
        
        for usuario_data in usuarios_data:
            password = usuario_data.pop('password')
            usuario = Usuario(**usuario_data)
            usuario.set_password(password)
            usuario.activo = True
            db.session.add(usuario)
        
        db.session.commit()
        print(f"   {len(usuarios_data)} usuarios creados")
        
        # ==================== CATEGORÍAS ====================
        print("Creando categorías...")
        categorias_data = [
            {'nombre': 'Motor', 'descripcion': 'Componentes del motor'},
            {'nombre': 'Transmisión', 'descripcion': 'Sistema de transmisión'},
            {'nombre': 'Suspensión', 'descripcion': 'Sistema de suspensión'},
            {'nombre': 'Frenos', 'descripcion': 'Sistema de frenado'},
            {'nombre': 'Eléctrico', 'descripcion': 'Sistema eléctrico'},
            {'nombre': 'Filtros', 'descripcion': 'Filtros de aceite, aire, combustible'},
            {'nombre': 'Iluminación', 'descripcion': 'Luces y sistemas de iluminación'},
            {'nombre': 'Carrocería', 'descripcion': 'Piezas de carrocería'}
        ]
        
        for cat_data in categorias_data:
            categoria = Categoria(**cat_data)
            db.session.add(categoria)
        
        db.session.commit()
        print(f"   {len(categorias_data)} categorías creadas")
        
        # ==================== AUTOPARTES ====================
        print("Creando autopartes...")
        
        # Obtener categorías
        cat_motor = Categoria.query.filter_by(nombre='Motor').first()
        cat_frenos = Categoria.query.filter_by(nombre='Frenos').first()
        cat_electrico = Categoria.query.filter_by(nombre='Eléctrico').first()
        cat_suspension = Categoria.query.filter_by(nombre='Suspensión').first()
        cat_filtros = Categoria.query.filter_by(nombre='Filtros').first()
        
        autopartes_data = [
            {'nombre': 'Filtro de Aceite Premium', 'descripcion': 'Filtro de aceite de alta eficiencia para motores modernos', 
             'categoria_id': cat_filtros.id, 'marca': 'Bosch', 'precio': 150.00, 'stock': 50, 'stock_min': 10},
            {'nombre': 'Pastillas de Freno Delanteras', 'descripcion': 'Pastillas cerámicas de alto rendimiento', 
             'categoria_id': cat_frenos.id, 'marca': 'Brembo', 'precio': 850.00, 'stock': 30, 'stock_min': 5},
            {'nombre': 'Alternador 12V 90A', 'descripcion': 'Alternador universal para vehículos compactos', 
             'categoria_id': cat_electrico.id, 'marca': 'Denso', 'precio': 2500.00, 'stock': 15, 'stock_min': 3},
            {'nombre': 'Amortiguador Trasero', 'descripcion': 'Amortiguador hidráulico para suspensión trasera', 
             'categoria_id': cat_suspension.id, 'marca': 'Monroe', 'precio': 1200.00, 'stock': 25, 'stock_min': 5},
            {'nombre': 'Bujías de Platino (Set 4)', 'descripcion': 'Set de 4 bujías de platino de larga duración', 
             'categoria_id': cat_motor.id, 'marca': 'NGK', 'precio': 450.00, 'stock': 40, 'stock_min': 8},
            {'nombre': 'Pastillas de Freno Traseras', 'descripcion': 'Pastillas cerámicas traseras', 
             'categoria_id': cat_frenos.id, 'marca': 'Brembo', 'precio': 650.00, 'stock': 28, 'stock_min': 5},
            {'nombre': 'Filtro de Aire de Alto Flujo', 'descripcion': 'Filtro de aire deportivo reutilizable', 
             'categoria_id': cat_filtros.id, 'marca': 'K&N', 'precio': 890.00, 'stock': 20, 'stock_min': 4},
            {'nombre': 'Batería 12V 60Ah', 'descripcion': 'Batería libre de mantenimiento', 
             'categoria_id': cat_electrico.id, 'marca': 'AC Delco', 'precio': 1850.00, 'stock': 12, 'stock_min': 3},
            {'nombre': 'Disco de Freno Ventilado', 'descripcion': 'Disco ventilado delantero par', 
             'categoria_id': cat_frenos.id, 'marca': 'Brembo', 'precio': 1950.00, 'stock': 8, 'stock_min': 4},
            {'nombre': 'Banda de Distribución', 'descripcion': 'Kit de banda de distribución completo', 
             'categoria_id': cat_motor.id, 'marca': 'Gates', 'precio': 1350.00, 'stock': 18, 'stock_min': 5}
        ]
        
        for ap_data in autopartes_data:
            stock_inicial = ap_data.pop('stock')
            stock_minimo = ap_data.pop('stock_min')
            
            autoparte = Autoparte(**ap_data)
            autoparte.activo = True
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
        print(f"   {len(autopartes_data)} autopartes creadas con inventario")
        
        # ==================== ESTADOS DE PEDIDO ====================
        print("Creando estados de pedido...")
        estados_data = [
            {'nombre': 'Pendiente'},
            {'nombre': 'En Proceso'},
            {'nombre': 'Preparando'},
            {'nombre': 'En Camino'},
            {'nombre': 'Entregado'},
            {'nombre': 'Cancelado'}
        ]
        
        for estado_data in estados_data:
            estado = EstadoPedido(**estado_data)
            db.session.add(estado)
        
        db.session.commit()
        print(f"   {len(estados_data)} estados creados")
        
        # ==================== PEDIDOS DE EJEMPLO ====================
        print("Creando pedidos de ejemplo...")
        
        usuario_ventas = Usuario.query.filter_by(email='ventas@macuin.com').first()
        estado_pendiente = EstadoPedido.query.filter_by(nombre='Pendiente').first()
        estado_proceso = EstadoPedido.query.filter_by(nombre='En Proceso').first()
        estado_entregado = EstadoPedido.query.filter_by(nombre='Entregado').first()
        
        # Pedido 1
        pedido1 = Pedido(
            usuario_id=usuario_ventas.id,
            estado_id=estado_pendiente.id,
            fecha_pedido=datetime.now(),
            total=0
        )
        db.session.add(pedido1)
        db.session.flush()
        
        autoparte1 = Autoparte.query.filter_by(nombre='Filtro de Aceite Premium').first()
        autoparte2 = Autoparte.query.filter_by(nombre='Pastillas de Freno Delanteras').first()
        
        detalle1 = DetallePedido(
            pedido_id=pedido1.id,
            autoparte_id=autoparte1.id,
            cantidad=2,
            precio_unitario=autoparte1.precio
        )
        db.session.add(detalle1)
        
        detalle2 = DetallePedido(
            pedido_id=pedido1.id,
            autoparte_id=autoparte2.id,
            cantidad=1,
            precio_unitario=autoparte2.precio
        )
        db.session.add(detalle2)
        
        pedido1.calcular_total()
        
        # Pedido 2
        pedido2 = Pedido(
            usuario_id=usuario_ventas.id,
            estado_id=estado_proceso.id,
            fecha_pedido=datetime.now(),
            total=0
        )
        db.session.add(pedido2)
        db.session.flush()
        
        autoparte3 = Autoparte.query.filter_by(nombre='Alternador 12V 90A').first()
        
        detalle3 = DetallePedido(
            pedido_id=pedido2.id,
            autoparte_id=autoparte3.id,
            cantidad=1,
            precio_unitario=autoparte3.precio
        )
        db.session.add(detalle3)
        
        pedido2.calcular_total()
        
        db.session.commit()
        print(f"   {len(pedido2.id if isinstance(pedido2.id, list) else [pedido2.id]) + 1} pedidos de ejemplo creados")
        
        # ==================== RESUMEN ====================
        print("\n" + "="*50)
        print("Base de datos inicializada correctamente!")
        print("="*50)
        print(f"\nResumen:")
        print(f"   - Roles: {Role.query.count()}")
        print(f"   - Usuarios: {Usuario.query.count()}")
        print(f"   - Categorías: {Categoria.query.count()}")
        print(f"   - Autopartes: {Autoparte.query.count()}")
        print(f"   - Inventarios: {Inventario.query.count()}")
        print(f"   - Estados: {EstadoPedido.query.count()}")
        print(f"   - Pedidos: {Pedido.query.count()}")
        
        print(f"\nCredenciales de acceso:")
        print(f"   Administrador:")
        print(f"   - Email: admin@macuin.com")
        print(f"   - Contraseña: admin123")
        print(f"\nVentas:")
        print(f"   - Email: ventas@macuin.com")
        print(f"   - Contraseña: ventas123")
        print(f"\n   Almacén:")
        print(f"   - Email: almacen@macuin.com")
        print(f"   - Contraseña: almacen123")
        print(f"\n   Logística:")
        print(f"   - Email: logistica@macuin.com")
        print(f"   - Contraseña: logistica123")
        print("\n" + "="*50)

if __name__ == '__main__':
    init_database()

"""Script de inicialización y sembrado de la base de datos"""
import sys
from app.data.db import engine, SessionLocal
from app.data.orm import Base, Role, Usuario, Categoria, Autoparte, Inventario, EstadoPedido
from app.security.auth import hash_password

def init():
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if db.query(Usuario).first():
            print("Base de datos ya inicializada. Omitiendo siembra.")
            return

        print("Sembrando datos iniciales...")

        # Roles
        roles = {}
        for nombre, desc in [
            ("Administrador", "Acceso completo al sistema"),
            ("Ventas", "Gestión de ventas y pedidos"),
            ("Almacén", "Gestión de inventario"),
            ("Logística", "Gestión de envíos y estados"),
        ]:
            r = Role(nombre=nombre, descripcion=desc)
            db.add(r)
            roles[nombre] = r
        db.flush()

        # Usuarios internos
        users_data = [
            ("Admin Macuin", "admin@macuin.com", "admin123", "Administrador"),
            ("Juan Ventas", "ventas@macuin.com", "ventas123", "Ventas"),
            ("Ana Almacén", "almacen@macuin.com", "almacen123", "Almacén"),
            ("Luis Logística", "logistica@macuin.com", "logistica123", "Logística"),
        ]
        for nombre, email, pwd, rol_nombre in users_data:
            u = Usuario(
                nombre=nombre, email=email,
                password_hash=hash_password(pwd),
                rol_id=roles[rol_nombre].id, activo=True,
            )
            db.add(u)
        db.flush()

        # Categorías
        cats = {}
        for nombre, desc in [
            ("Motor", "Componentes del motor"),
            ("Frenos", "Sistema de frenos"),
            ("Suspensión", "Sistema de suspensión"),
            ("Eléctrico", "Sistema eléctrico"),
            ("Carrocería", "Partes de carrocería"),
        ]:
            c = Categoria(nombre=nombre, descripcion=desc)
            db.add(c)
            cats[nombre] = c
        db.flush()

        # Autopartes e inventario
        parts = [
            ("Filtro de Aceite", "Motor", "Bosch", 150.00, "Filtro de aceite alta eficiencia", 50, 10),
            ("Pastillas de Freno Delanteras", "Frenos", "Brembo", 850.00, "Pastillas cerámicas larga duración", 30, 5),
            ("Amortiguador Delantero", "Suspensión", "Monroe", 1200.00, "Amortiguador reforzado", 5, 10),
            ("Batería 12V 60Ah", "Eléctrico", "Varta", 2500.00, "Batería libre de mantenimiento", 15, 3),
            ("Disco de Freno", "Frenos", "ATE", 620.00, "Disco ventilado alta resistencia", 20, 4),
            ("Bujías NGK (x4)", "Motor", "NGK", 280.00, "Bujías iridio alto rendimiento", 40, 8),
            ("Correa de Distribución", "Motor", "Gates", 450.00, "Kit correa distribución completo", 25, 5),
            ("Filtro de Aire", "Motor", "Mann", 95.00, "Filtro alta filtración", 60, 15),
            ("Sensor de Oxígeno", "Eléctrico", "Bosch", 780.00, "Sonda lambda universal", 10, 2),
            ("Retrovisor Lateral Der.", "Carrocería", "TYC", 320.00, "Retrovisor eléctrico con calefacción", 8, 2),
        ]
        for nombre, cat, marca, precio, desc, stock, stock_min in parts:
            a = Autoparte(
                nombre=nombre, categoria_id=cats[cat].id, marca=marca,
                precio=precio, descripcion=desc, activo=True,
            )
            db.add(a)
            db.flush()
            db.add(Inventario(autoparte_id=a.id, stock_actual=stock, stock_minimo=stock_min))

        # Estados de pedido
        estados = {}
        for nombre in ["Pendiente", "En Proceso", "Entregado", "Cancelado"]:
            e = EstadoPedido(nombre=nombre)
            db.add(e)
            estados[nombre] = e

        db.commit()
        print("Datos sembrados exitosamente.")
        print("\nCredenciales de acceso:")
        print("  Admin:     admin@macuin.com / admin123")
        print("  Ventas:    ventas@macuin.com / ventas123")
        print("  Almacén:   almacen@macuin.com / almacen123")
        print("  Logística: logistica@macuin.com / logistica123")

    except Exception as e:
        db.rollback()
        print(f"Error en siembra: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    init()

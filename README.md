# Macuin — Sistema de Gestión de Autopartes
Sistema web integral para la gestión de inventario, ventas y pedidos de una comercializadora de autopartes. El sistema permite el control total desde la entrada de productos al almacén hasta la compra final por parte del cliente externo.

## Arquitectura del Sistema
El proyecto está compuesto por tres aplicaciones independientes que se comunican a través de una API centralizada y comparten una base de datos PostgreSQL.

**Macuin/**
├── **FastAPI/** # API Central (Python/FastAPI) → Puerto 8080
├── **Flask/** # Sistema Interno - Empleados (Python/Flask) → Puerto 5000
├── **Laravel/** # Sistema Externo - Clientes (PHP/Laravel) → Puerto 8000
└── **docker-compose.yml** # Orquestación completa con Docker

| Sistema | Tecnología | Puerto | Usuarios |
| :--- | :--- | :--- | :--- |
| **FastAPI** | Python 3.12 + FastAPI | 8080 | API Central / Docs |
| **Flask** | Python 3.12 + Flask 3.1 | 5000 | Administrador, Almacén, Ventas, Logística |
| **Laravel** | PHP 8.4 + Laravel 12 | 8000 | Clientes Externos |
| **PostgreSQL**| PostgreSQL 16 | 5432 | (Base de datos central) |

---

## Módulos del Sistema

### Flask — Sistema Interno (Personal Macuin)
Destinado a la operación diaria del negocio. El acceso está restringido por roles.

| Módulo | Descripción |
| :--- | :--- |
| **Dashboard** | Resumen de stock, pedidos pendientes y gráficas de ventas recientes. |
| **Autopartes** | Catálogo maestro de productos, marcas y categorías. |
| **Inventario** | Control de existencias, gestión de entradas/salidas y alertas de stock bajo. |
| **Pedidos** | Registro de pedidos realizados en mostrador y seguimiento de estados. |
| **Reportes** | Generación de reportes en **PDF, Excel (XLSX) y Word (DOCX)**. |
| **Usuarios** | Gestión de empleados y asignación de roles de acceso. |

### Laravel — Sistema Externo (Portal de Clientes)
Enfocado en el cliente final para facilitar la consulta y compra de autopartes.

| Módulo | Descripción |
| :--- | :--- |
| **Catálogo** | Búsqueda dinámica de autopartes por nombre, marca o categoría. |
| **Pedidos** | Realización de pedidos en línea con historial de compras. |
| **Perfil** | Gestión de datos personales, dirección y contacto del cliente. |
| **Registro** | Creación de cuentas para nuevos clientes externos. |

---

## Reportes Disponibles
El sistema genera documentos profesionales en múltiples formatos para la toma de decisiones:
*   **Ventas Totales:** Consolidado de operaciones internas y externas con filtros de fecha.
*   **Inventario Actual:** Listado con valoración de stock y alertas de reabastecimiento.
*   **Estado de Pedidos:** Seguimiento detallado de órdenes pendientes, en proceso o entregadas.
*   **Usuarios y Clientes:** Directorio completo de personal y base de datos de clientes.
*   **Top Ventas:** Ranking de las autopartes más vendidas y su impacto en ingresos.

---

## Requisitos
*   **Docker** + **Docker Compose**
*   **Git**

---

## Guía de Instalación

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd macuin
```

### 2. Construir y levantar los contenedores
```bash
docker compose up -d --build
```
Este comando levantará los cuatro servicios: `macuin_postgres`, `macuin_fastapi`, `macuin_flask` y `macuin_laravel`.

### 3. Inicializar la base de datos
Una vez que los contenedores estén corriendo, ejecuta el script de inicialización en el contenedor de FastAPI para crear las tablas y sembrar los datos iniciales:
```bash
docker compose exec fastapi python init_db.py
```

### 4. Configurar Laravel
Ejecuta las migraciones base de Laravel (para sesiones y caché):
```bash
docker compose exec laravel php artisan migrate --force
```

---

## Acceso a los Sistemas

| Sistema | URL | Usuario | Contraseña |
| :--- | :--- | :--- | :--- |
| **Sistema Interno (Flask)** | `http://localhost:5000` | `admin@macuin.com` | `admin123` |
| **Portal Clientes (Laravel)** | `http://localhost:8000` | (Requiere Registro) | - |
| **Documentación API** | `http://localhost:8080/docs` | - | - |

**Credenciales de prueba para roles internos:**
*   **Ventas:** `ventas@macuin.com` / `ventas123`
*   **Almacén:** `almacen@macuin.com` / `almacen123`
*   **Logística:** `logistica@macuin.com` / `logistica123`

---

## Comandos Útiles

**Ver logs de un servicio:**
```bash
docker compose logs -f fastapi
docker compose logs -f flask
docker compose logs -f laravel
```

**Reiniciar la base de datos (Borra todos los datos):**
```bash
docker compose down -v
docker compose up -d
docker compose exec fastapi python init_db.py
```

**Acceder a la consola de PostgreSQL:**
```bash
docker compose exec postgres psql -U admin -d macuin_db
```

---

## Base de Datos
La base de datos se gestiona centralizadamente desde **FastAPI** utilizando SQLAlchemy. Se inicializa automáticamente con el script `init_db.py`.

### Tablas Principales
| Tabla | Descripción |
| :--- | :--- |
| **roles** | Definición de roles (Admin, Ventas, Almacén, Logística). |
| **usuarios** | Personal interno con acceso al sistema Flask. |
| **categorias** | Clasificación de las autopartes. |
| **autopartes** | Catálogo maestro de productos con precios y marcas. |
| **inventarios** | Control de stock actual y niveles mínimos por autoparte. |
| **estados_pedido** | Estados del flujo de pedidos (Pendiente, En Proceso, etc.). |
| **pedidos** | Cabecera de órdenes generadas internamente. |
| **detalle_pedido** | Ítems y cantidades de cada pedido interno. |
| **clientes** | Usuarios externos registrados desde el portal Laravel. |
| **pedidos_externos** | Órdenes realizadas por clientes finales. |
| **detalle_pedido_externo**| Ítems de las órdenes externas. |

---

## Stack Tecnológico

### Backend & API
*   **FastAPI:** Framework de alto rendimiento con validación de datos Pydantic.
*   **SQLAlchemy:** ORM para la gestión de la base de datos PostgreSQL.
*   **ReportLab / OpenPyXL / Python-Docx:** Motores de generación de reportes profesionales.

### Frontend
*   **Flask + Jinja2:** Plantillas dinámicas con Bootstrap 5 para el sistema interno.
*   **Laravel + Blade:** Motor de plantillas moderno para la experiencia del cliente.
*   **Bootstrap 5:** Diseño responsivo y componentes modernos en ambas plataformas.

### Infraestructura
*   **Docker:** Contenerización de servicios para un despliegue consistente.
*   **PostgreSQL 16:** Base de datos relacional robusta.

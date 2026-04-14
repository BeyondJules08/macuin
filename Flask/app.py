import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, Response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from functools import wraps
import requests as http_requests

import api_client as api
from api_client import to_obj

# ── User class (no DB) ───────────────────────────────────────────────

from flask_login import UserMixin
from flask import session


class User(UserMixin):
    def __init__(self, data: dict):
        self.id = data["id"]
        self.nombre = data["nombre"]
        self.email = data["email"]
        self.activo = data.get("activo", True)
        rol_nombre = data.get("rol") or data.get("rol_nombre", "")
        self.rol = type("Rol", (), {"nombre": rol_nombre})()


# ── App factory ──────────────────────────────────────────────────────

def create_app():
    app = Flask(__name__)
    app.secret_key = os.getenv("SECRET_KEY", "macuin_flask_secret_2024")
    app.config["ITEMS_PER_PAGE"] = 20

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "login"
    login_manager.login_message = "Por favor inicia sesión."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id):
        user_data = session.get("user_data")
        if user_data and str(user_data.get("id")) == str(user_id):
            return User(user_data)
        return None

    def role_required(*role_names):
        def decorator(f):
            @wraps(f)
            def decorated(*args, **kwargs):
                if not current_user.is_authenticated:
                    return redirect(url_for("login"))
                if (
                    current_user.rol.nombre not in role_names
                    and current_user.rol.nombre != "Administrador"
                ):
                    flash("No tienes permisos para acceder a esta página.", "danger")
                    return redirect(url_for("dashboard"))
                return f(*args, **kwargs)
            return decorated
        return decorator

    @app.context_processor
    def inject_user():
        return dict(current_user=current_user)

    # ── Auth ──────────────────────────────────────────────────────────

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            email = request.form.get("email")
            password = request.form.get("password")
            remember = bool(request.form.get("remember"))
            result = api.login_usuario(email, password)
            if result and result.get("status") == "200":
                user_data = result["data"]
                session["user_data"] = user_data
                user = User(user_data)
                login_user(user, remember=remember)
                flash(f"Bienvenido {user.nombre}!", "success")
                next_page = request.args.get("next")
                return redirect(next_page or url_for("dashboard"))
            else:
                flash("Email o contraseña incorrectos.", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        session.pop("user_data", None)
        logout_user()
        flash("Has cerrado sesión exitosamente.", "info")
        return redirect(url_for("login"))

    # ── Dashboard ─────────────────────────────────────────────────────

    @app.route("/dashboard")
    @login_required
    def dashboard():
        try:
            stats = api.get_dashboard_stats()
            # Build compatible objects for templates
            productos_bajo_stock = [
                (to_obj({
                    "id": i.autoparte_id,
                    "nombre": i.autoparte_nombre,
                    "marca": i.autoparte_marca,
                }), i)
                for i in stats["bajo_stock_items"]
            ]
            return render_template(
                "dashboard.html",
                total_autopartes=stats["total_autopartes"],
                total_pedidos=stats["total_pedidos"],
                pedidos_pendientes=stats["pedidos_pendientes"],
                productos_bajo_stock=productos_bajo_stock,
                pedidos_recientes=stats["pedidos_recientes"],
                ventas_mes=stats["ventas_mes"],
            )
        except Exception as e:
            flash(f"Error al cargar dashboard: {e}", "danger")
            return render_template(
                "dashboard.html",
                total_autopartes=0, total_pedidos=0, pedidos_pendientes=0,
                productos_bajo_stock=[], pedidos_recientes=[], ventas_mes=0,
            )

    # ── Autopartes ────────────────────────────────────────────────────

    @app.route("/autopartes")
    @login_required
    def autopartes_list():
        page = request.args.get("page", 1, type=int)
        search = request.args.get("search", "")
        categoria_id = request.args.get("categoria", type=int)
        try:
            autopartes = api.get_autopartes(page, app.config["ITEMS_PER_PAGE"], search, categoria_id)
            categorias = api.get_categorias()
        except Exception as e:
            flash(f"Error al cargar autopartes: {e}", "danger")
            from api_client import Pagination
            autopartes = Pagination([], 1, 20, 0)
            categorias = []
        return render_template(
            "autopartes/list.html",
            autopartes=autopartes,
            categorias=categorias,
            search=search,
            categoria_id=categoria_id,
        )

    @app.route("/autopartes/crear", methods=["GET", "POST"])
    @login_required
    @role_required("Administrador", "Almacén")
    def autopartes_create():
        if request.method == "POST":
            payload = {
                "nombre": request.form.get("nombre"),
                "descripcion": request.form.get("descripcion"),
                "categoria_id": int(request.form.get("categoria_id", 0)),
                "marca": request.form.get("marca"),
                "precio": float(request.form.get("precio", 0)),
                "stock_inicial": int(request.form.get("stock_inicial", 0)),
                "stock_minimo": int(request.form.get("stock_minimo", 0)),
                "activo": True,
            }
            try:
                api.create_autoparte(payload)
                flash("Autoparte creada exitosamente.", "success")
                return redirect(url_for("autopartes_list"))
            except Exception as e:
                flash(f"Error: {e}", "danger")
        categorias = api.get_categorias()
        return render_template("autopartes/form.html", categorias=categorias)

    @app.route("/autopartes/<int:id>/editar", methods=["GET", "POST"])
    @login_required
    @role_required("Administrador", "Almacén")
    def autopartes_edit(id):
        try:
            autoparte = api.get_autoparte(id)
        except Exception:
            flash("Autoparte no encontrada.", "danger")
            return redirect(url_for("autopartes_list"))

        if request.method == "POST":
            payload = {
                "nombre": request.form.get("nombre"),
                "descripcion": request.form.get("descripcion"),
                "categoria_id": int(request.form.get("categoria_id", 0)),
                "marca": request.form.get("marca"),
                "precio": float(request.form.get("precio", 0)),
                "activo": request.form.get("activo") == "on",
            }
            try:
                api.update_autoparte(id, payload)
                flash("Autoparte actualizada exitosamente.", "success")
                return redirect(url_for("autopartes_list"))
            except Exception as e:
                flash(f"Error: {e}", "danger")

        categorias = api.get_categorias()
        return render_template("autopartes/form.html", autoparte=autoparte, categorias=categorias)

    @app.route("/autopartes/<int:id>/eliminar", methods=["POST"])
    @login_required
    @role_required("Administrador")
    def autopartes_delete(id):
        try:
            api.delete_autoparte(id)
            flash("Autoparte desactivada exitosamente.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        return redirect(url_for("autopartes_list"))

    # ── Inventario ────────────────────────────────────────────────────

    @app.route("/inventario")
    @login_required
    @role_required("Administrador", "Almacén")
    def inventario_list():
        page = request.args.get("page", 1, type=int)
        search = request.args.get("search", "")
        bajo_stock = request.args.get("bajo_stock") == "True"
        try:
            inventarios = api.get_inventario(page, app.config["ITEMS_PER_PAGE"], search, bajo_stock)
        except Exception as e:
            flash(f"Error: {e}", "danger")
            from api_client import Pagination
            inventarios = Pagination([], 1, 20, 0)
        return render_template("inventario/list.html", inventarios=inventarios, search=search, bajo_stock=bajo_stock)

    @app.route("/inventario/<int:id>/actualizar", methods=["GET", "POST"])
    @login_required
    @role_required("Administrador", "Almacén")
    def inventario_update(id):
        try:
            inventario = api.get_inventario_item(id)
        except Exception:
            flash("Inventario no encontrado.", "danger")
            return redirect(url_for("inventario_list"))

        if request.method == "POST":
            payload = {
                "operacion": request.form.get("operacion"),
                "cantidad": int(request.form.get("cantidad", 0)),
                "stock_minimo": int(request.form.get("stock_minimo", inventario.stock_minimo)),
            }
            try:
                api.update_inventario(id, payload)
                flash("Inventario actualizado exitosamente.", "success")
                return redirect(url_for("inventario_list"))
            except Exception as e:
                flash(f"Error: {e}", "danger")

        return render_template("inventario/update.html", inventario=inventario)

    # ── Pedidos ───────────────────────────────────────────────────────

    @app.route("/pedidos")
    @login_required
    def pedidos_list():
        page = request.args.get("page", 1, type=int)
        estado_id = request.args.get("estado", type=int)
        usuario_id = None
        if current_user.rol.nombre == "Ventas":
            usuario_id = current_user.id
        try:
            pedidos = api.get_pedidos(page, app.config["ITEMS_PER_PAGE"], estado_id, usuario_id)
            estados = api.get_estados_pedido()
        except Exception as e:
            flash(f"Error: {e}", "danger")
            from api_client import Pagination
            pedidos = Pagination([], 1, 20, 0)
            estados = []
        return render_template("pedidos/list.html", pedidos=pedidos, estados=estados, estado_id=estado_id)

    @app.route("/pedidos/crear", methods=["GET", "POST"])
    @login_required
    @role_required("Administrador", "Ventas")
    def pedidos_create():
        if request.method == "POST":
            autoparte_ids = request.form.getlist("autoparte_id[]")
            cantidades = request.form.getlist("cantidad[]")
            items = []
            for ap_id, cant in zip(autoparte_ids, cantidades):
                if ap_id and cant:
                    items.append({"autoparte_id": int(ap_id), "cantidad": int(cant)})
            if not items:
                flash("Agrega al menos un producto.", "danger")
            else:
                try:
                    api.create_pedido(current_user.id, items)
                    flash("Pedido creado exitosamente.", "success")
                    return redirect(url_for("pedidos_list"))
                except Exception as e:
                    flash(f"Error: {e}", "danger")

        try:
            autopartes = api.get_autopartes_activas()
        except Exception:
            autopartes = []
        return render_template("pedidos/form.html", autopartes=autopartes)

    @app.route("/pedidos/<int:id>")
    @login_required
    def pedidos_detail(id):
        try:
            pedido = api.get_pedido(id)
        except Exception:
            flash("Pedido no encontrado.", "danger")
            return redirect(url_for("pedidos_list"))
        if current_user.rol.nombre == "Ventas" and pedido.usuario_id != current_user.id:
            flash("No tienes permisos para ver este pedido.", "danger")
            return redirect(url_for("pedidos_list"))
        return render_template("pedidos/detail.html", pedido=pedido)

    @app.route("/pedidos/<int:id>/cambiar-estado", methods=["POST"])
    @login_required
    @role_required("Administrador", "Logística")
    def pedidos_change_status(id):
        nuevo_estado_id = request.form.get("estado_id", type=int)
        try:
            api.cambiar_estado_pedido(id, nuevo_estado_id)
            flash("Estado del pedido actualizado.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        return redirect(url_for("pedidos_detail", id=id))

    # ── Usuarios ──────────────────────────────────────────────────────

    @app.route("/usuarios")
    @login_required
    @role_required("Administrador")
    def usuarios_list():
        try:
            usuarios = api.get_usuarios()
        except Exception as e:
            flash(f"Error: {e}", "danger")
            usuarios = []
        return render_template("usuarios/list.html", usuarios=usuarios)

    @app.route("/usuarios/crear", methods=["GET", "POST"])
    @login_required
    @role_required("Administrador")
    def usuarios_create():
        if request.method == "POST":
            payload = {
                "nombre": request.form.get("nombre"),
                "email": request.form.get("email"),
                "password": request.form.get("password"),
                "rol_id": int(request.form.get("rol_id", 1)),
                "activo": True,
            }
            try:
                api.create_usuario(payload)
                flash("Usuario creado exitosamente.", "success")
                return redirect(url_for("usuarios_list"))
            except Exception as e:
                flash(f"Error: {e}", "danger")
        roles = api.get_roles()
        return render_template("usuarios/form.html", roles=roles)

    @app.route("/usuarios/<int:id>/editar", methods=["GET", "POST"])
    @login_required
    @role_required("Administrador")
    def usuarios_edit(id):
        try:
            usuario = api.get_usuario(id)
        except Exception:
            flash("Usuario no encontrado.", "danger")
            return redirect(url_for("usuarios_list"))

        if request.method == "POST":
            payload = {
                "nombre": request.form.get("nombre"),
                "email": request.form.get("email"),
                "rol_id": int(request.form.get("rol_id", 1)),
                "activo": request.form.get("activo") == "on",
            }
            new_pwd = request.form.get("password")
            if new_pwd:
                payload["password"] = new_pwd
            try:
                api.update_usuario(id, payload)
                flash("Usuario actualizado exitosamente.", "success")
                return redirect(url_for("usuarios_list"))
            except Exception as e:
                flash(f"Error: {e}", "danger")

        roles = api.get_roles()
        return render_template("usuarios/form.html", usuario=usuario, roles=roles)

    @app.route("/usuarios/<int:id>/eliminar", methods=["POST"])
    @login_required
    @role_required("Administrador")
    def usuarios_delete(id):
        try:
            api.delete_usuario(id)
            flash("Usuario eliminado exitosamente.", "success")
        except Exception as e:
            flash(f"Error: {e}", "danger")
        return redirect(url_for("usuarios_list"))

    # ── Reportes ──────────────────────────────────────────────────────

    @app.route("/reportes")
    @login_required
    @role_required("Administrador", "Ventas", "Logística")
    def reportes_list():
        return render_template("reportes/list.html")

    @app.route("/reportes/<tipo>")
    @login_required
    @role_required("Administrador", "Ventas", "Logística")
    def reporte_descargar(tipo):
        tipos_validos = {"ventas", "inventario", "pedidos", "usuarios", "autopartes-mas-vendidas"}
        if tipo not in tipos_validos:
            flash("Tipo de reporte inválido.", "danger")
            return redirect(url_for("reportes_list"))

        formato = request.args.get("formato", "pdf")
        params = {"formato": formato}
        if tipo == "ventas":
            if request.args.get("fecha_inicio"):
                params["fecha_inicio"] = request.args.get("fecha_inicio")
            if request.args.get("fecha_fin"):
                params["fecha_fin"] = request.args.get("fecha_fin")
        if tipo == "pedidos" and request.args.get("estado"):
            params["estado_nombre"] = request.args.get("estado")

        try:
            resp = api._stream(f"/v1/reportes/{tipo}", params)
            content_type = resp.headers.get("content-type", "application/octet-stream")
            content_disp = resp.headers.get("content-disposition", f'attachment; filename="reporte.{formato}"')
            return Response(
                resp.iter_content(chunk_size=4096),
                content_type=content_type,
                headers={"Content-Disposition": content_disp},
            )
        except Exception as e:
            flash(f"Error al generar reporte: {e}", "danger")
            return redirect(url_for("reportes_list"))

    # ── API interna ───────────────────────────────────────────────────

    @app.route("/api/autopartes/buscar")
    @login_required
    def api_autopartes_search():
        q = request.args.get("q", "")
        try:
            return jsonify(api.search_autopartes(q))
        except Exception:
            return jsonify([])

    @app.route("/api/estadisticas")
    @login_required
    def api_statistics():
        try:
            stats = api.get_dashboard_stats()
            return jsonify({
                "total_autopartes": stats["total_autopartes"],
                "total_pedidos": stats["total_pedidos"],
                "bajo_stock": len(stats["bajo_stock_items"]),
            })
        except Exception:
            return jsonify({"total_autopartes": 0, "total_pedidos": 0, "bajo_stock": 0})

    # ── Error handlers ────────────────────────────────────────────────

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(e):
        return render_template("errors/500.html"), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)

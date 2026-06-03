from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from functools import wraps
from datetime import date, datetime, time
from app import db
from app.models import Usuario, Servicio, Horario, Reserva, Notificacion, Pago

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            flash("Acceso restringido a administradores.", "danger")
            return redirect(url_for("main.index"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def dashboard():
    stats = {
        "usuarios": Usuario.query.filter_by(activo=True).count(),
        "servicios": Servicio.query.filter_by(activo=True).count(),
        "reservas_hoy": Reserva.query.join(Horario).filter(
            Horario.fecha == date.today()
        ).count(),
        "reservas_total": Reserva.query.filter_by(estado="confirmada").count(),
        "cancelaciones": Reserva.query.filter_by(estado="cancelada").count(),
    }
    reservas_recientes = Reserva.query.order_by(Reserva.fecha_reserva.desc()).limit(10).all()
    return render_template("admin/dashboard.html", stats=stats, reservas_recientes=reservas_recientes)


# ---- SERVICIOS ----
@admin_bp.route("/servicios")
@admin_required
def servicios():
    servicios = Servicio.query.order_by(Servicio.id.desc()).all()
    return render_template("admin/servicios.html", servicios=servicios)


@admin_bp.route("/servicios/nuevo", methods=["GET", "POST"])
@admin_required
def servicio_nuevo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        duracion = int(request.form.get("duracion_minutos", 60))
        precio = float(request.form.get("precio", 0))
        categoria = request.form.get("categoria", "").strip()

        if not nombre:
            flash("El nombre es obligatorio.", "danger")
            return render_template("admin/servicio_form.html", servicio=None)

        servicio = Servicio(
            nombre=nombre, descripcion=descripcion, duracion_minutos=duracion,
            precio=precio, categoria=categoria
        )
        db.session.add(servicio)
        db.session.commit()
        flash("Servicio creado correctamente.", "success")
        return redirect(url_for("admin.servicios"))

    return render_template("admin/servicio_form.html", servicio=None)


@admin_bp.route("/servicios/editar/<int:sid>", methods=["GET", "POST"])
@admin_required
def servicio_editar(sid):
    servicio = Servicio.query.get_or_404(sid)

    if request.method == "POST":
        servicio.nombre = request.form.get("nombre", servicio.nombre).strip()
        servicio.descripcion = request.form.get("descripcion", "").strip()
        servicio.duracion_minutos = int(request.form.get("duracion_minutos", 60))
        servicio.precio = float(request.form.get("precio", 0))
        servicio.categoria = request.form.get("categoria", "").strip()
        servicio.activo = request.form.get("activo") == "on"
        db.session.commit()
        flash("Servicio actualizado.", "success")
        return redirect(url_for("admin.servicios"))

    return render_template("admin/servicio_form.html", servicio=servicio)


@admin_bp.route("/servicios/eliminar/<int:sid>", methods=["POST"])
@admin_required
def servicio_eliminar(sid):
    servicio = Servicio.query.get_or_404(sid)
    servicio.activo = False
    db.session.commit()
    flash("Servicio desactivado.", "info")
    return redirect(url_for("admin.servicios"))


# ---- HORARIOS ----
@admin_bp.route("/horarios")
@admin_required
def horarios():
    horarios = Horario.query.order_by(Horario.fecha.desc(), Horario.hora_inicio).all()
    servicios = Servicio.query.filter_by(activo=True).all()
    return render_template("admin/horarios.html", horarios=horarios, servicios=servicios)


@admin_bp.route("/horarios/nuevo", methods=["GET", "POST"])
@admin_required
def horario_nuevo():
    servicios = Servicio.query.filter_by(activo=True).all()

    if request.method == "POST":
        servicio_id = int(request.form.get("servicio_id"))
        fecha_str = request.form.get("fecha")
        hora_inicio_str = request.form.get("hora_inicio")
        hora_fin_str = request.form.get("hora_fin")
        cupos = int(request.form.get("cupos_totales", 1))
        responsable = request.form.get("responsable", "").strip()

        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            hora_inicio = datetime.strptime(hora_inicio_str, "%H:%M").time()
            hora_fin = datetime.strptime(hora_fin_str, "%H:%M").time()
        except ValueError:
            flash("Formato de fecha u hora inválido.", "danger")
            return render_template("admin/horario_form.html", servicios=servicios, horario=None)

        horario = Horario(
            servicio_id=servicio_id, fecha=fecha, hora_inicio=hora_inicio,
            hora_fin=hora_fin, cupos_totales=cupos, cupos_disponibles=cupos,
            responsable=responsable
        )
        db.session.add(horario)
        db.session.commit()
        flash("Horario creado correctamente.", "success")
        return redirect(url_for("admin.horarios"))

    return render_template("admin/horario_form.html", servicios=servicios, horario=None)


@admin_bp.route("/horarios/eliminar/<int:hid>", methods=["POST"])
@admin_required
def horario_eliminar(hid):
    horario = Horario.query.get_or_404(hid)
    horario.activo = False
    db.session.commit()
    flash("Horario desactivado.", "info")
    return redirect(url_for("admin.horarios"))


# ---- USUARIOS ----
@admin_bp.route("/usuarios")
@admin_required
def usuarios():
    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).all()
    return render_template("admin/usuarios.html", usuarios=usuarios)


@admin_bp.route("/usuarios/toggle/<int:uid>", methods=["POST"])
@admin_required
def usuario_toggle(uid):
    usuario = Usuario.query.get_or_404(uid)
    if usuario.id == current_user.id:
        flash("No puedes desactivar tu propia cuenta.", "warning")
    else:
        usuario.activo = not usuario.activo
        db.session.commit()
        estado = "activado" if usuario.activo else "desactivado"
        flash(f"Usuario {estado} correctamente.", "info")
    return redirect(url_for("admin.usuarios"))


@admin_bp.route("/usuarios/rol/<int:uid>", methods=["POST"])
@admin_required
def usuario_rol(uid):
    usuario = Usuario.query.get_or_404(uid)
    nuevo_rol = request.form.get("rol", "usuario")
    if nuevo_rol in ("usuario", "empleado", "admin"):
        usuario.rol = nuevo_rol
        db.session.commit()
        flash("Rol actualizado.", "success")
    return redirect(url_for("admin.usuarios"))


# ---- RESERVAS ----
@admin_bp.route("/reservas")
@admin_required
def reservas():
    reservas = Reserva.query.order_by(Reserva.fecha_reserva.desc()).all()
    return render_template("admin/reservas.html", reservas=reservas)


# ---- REPORTES ----
@admin_bp.route("/reportes")
@admin_required
def reportes():
    # Reservas por servicio
    from sqlalchemy import func
    por_servicio = db.session.query(
        Servicio.nombre,
        func.count(Reserva.id).label("total")
    ).join(Horario, Horario.servicio_id == Servicio.id)\
     .join(Reserva, Reserva.horario_id == Horario.id)\
     .group_by(Servicio.nombre).all()

    stats = {
        "total_reservas": Reserva.query.count(),
        "confirmadas": Reserva.query.filter_by(estado="confirmada").count(),
        "canceladas": Reserva.query.filter_by(estado="cancelada").count(),
        "completadas": Reserva.query.filter_by(estado="completada").count(),
        "usuarios_activos": Usuario.query.filter_by(activo=True).count(),
    }

    return render_template("admin/reportes.html", stats=stats, por_servicio=por_servicio)

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, date
import secrets
from app import db
from app.models import Servicio, Horario, Reserva, Notificacion
from app.utils.email import enviar_confirmacion, enviar_cancelacion

reservas_bp = Blueprint("reservas", __name__)


def generar_codigo():
    return "RES-" + secrets.token_hex(4).upper()


@reservas_bp.route("/")
@login_required
def mis_reservas():
    reservas = Reserva.query.filter_by(usuario_id=current_user.id)\
        .order_by(Reserva.fecha_reserva.desc()).all()
    return render_template("reservas/mis_reservas.html", reservas=reservas)


@reservas_bp.route("/nueva/<int:servicio_id>")
@login_required
def nueva(servicio_id):
    servicio = Servicio.query.get_or_404(servicio_id)
    hoy = date.today()
    horarios = Horario.query.filter(
        Horario.servicio_id == servicio_id,
        Horario.fecha >= hoy,
        Horario.activo == True,
        Horario.cupos_disponibles > 0
    ).order_by(Horario.fecha, Horario.hora_inicio).all()
    return render_template("reservas/nueva.html", servicio=servicio, horarios=horarios)


@reservas_bp.route("/confirmar/<int:horario_id>", methods=["GET", "POST"])
@login_required
def confirmar(horario_id):
    horario = Horario.query.get_or_404(horario_id)

    if not horario.disponible:
        flash("Lo sentimos, este horario ya no está disponible.", "warning")
        return redirect(url_for("reservas.nueva", servicio_id=horario.servicio_id))

    # Verificar que no tenga ya una reserva en este horario
    existente = Reserva.query.filter_by(
        usuario_id=current_user.id,
        horario_id=horario_id,
        estado="confirmada"
    ).first()
    if existente:
        flash("Ya tienes una reserva en este horario.", "warning")
        return redirect(url_for("reservas.mis_reservas"))

    if request.method == "POST":
        nombre = request.form.get("nombre", current_user.nombre)
        telefono = request.form.get("telefono", current_user.telefono or "")
        correo = request.form.get("correo", current_user.correo)
        notas = request.form.get("notas", "")

        reserva_notas = (
            f"Cliente: {nombre}\n"
            f"Teléfono: {telefono}\n"
            f"Correo: {correo}\n"
            f"Notas: {notas}"
        ).strip()

        reserva = Reserva(
            usuario_id=current_user.id,
            horario_id=horario_id,
            estado="confirmada",
            notas=reserva_notas,
            codigo=generar_codigo()
        )
        horario.cupos_disponibles -= 1
        db.session.add(reserva)

        # Notificación interna
        notif = Notificacion(
            usuario_id=current_user.id,
            tipo="confirmacion",
            mensaje=f"Tu reserva {reserva.codigo} para {horario.servicio.nombre} el {horario.fecha} fue confirmada.",
            canal="sistema"
        )
        db.session.add(notif)
        db.session.commit()

        try:
            enviar_confirmacion(current_user, reserva)
        except Exception:
            pass

        flash(f"¡Reserva confirmada! Tu código es: {reserva.codigo}", "success")
        return redirect(url_for("reservas.detalle", reserva_id=reserva.id))

    return render_template("reservas/confirmar.html", horario=horario)


@reservas_bp.route("/detalle/<int:reserva_id>")
@login_required
def detalle(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)
    if reserva.usuario_id != current_user.id and not current_user.is_empleado:
        flash("No tienes permiso para ver esta reserva.", "danger")
        return redirect(url_for("reservas.mis_reservas"))
    return render_template("reservas/detalle.html", reserva=reserva)


@reservas_bp.route("/cancelar/<int:reserva_id>", methods=["POST"])
@login_required
def cancelar(reserva_id):
    reserva = Reserva.query.get_or_404(reserva_id)

    if reserva.usuario_id != current_user.id and not current_user.is_empleado:
        flash("No tienes permiso.", "danger")
        return redirect(url_for("reservas.mis_reservas"))

    if reserva.estado != "confirmada":
        flash("Esta reserva no puede cancelarse.", "warning")
        return redirect(url_for("reservas.mis_reservas"))

    motivo = request.form.get("motivo", "Sin motivo especificado")
    reserva.estado = "cancelada"
    reserva.fecha_cancelacion = datetime.utcnow()
    reserva.motivo_cancelacion = motivo
    reserva.horario.cupos_disponibles += 1

    notif = Notificacion(
        usuario_id=current_user.id,
        tipo="cancelacion",
        mensaje=f"Tu reserva {reserva.codigo} ha sido cancelada.",
        canal="sistema"
    )
    db.session.add(notif)
    db.session.commit()

    try:
        enviar_cancelacion(current_user, reserva)
    except Exception:
        pass

    flash("Reserva cancelada correctamente.", "info")
    return redirect(url_for("reservas.mis_reservas"))


@reservas_bp.route("/api/horarios/<int:servicio_id>")
@login_required
def api_horarios(servicio_id):
    hoy = date.today()
    horarios = Horario.query.filter(
        Horario.servicio_id == servicio_id,
        Horario.fecha >= hoy,
        Horario.activo == True,
        Horario.cupos_disponibles > 0
    ).order_by(Horario.fecha, Horario.hora_inicio).all()

    data = [{
        "id": h.id,
        "fecha": h.fecha.strftime("%d/%m/%Y"),
        "hora_inicio": h.hora_inicio.strftime("%H:%M"),
        "hora_fin": h.hora_fin.strftime("%H:%M"),
        "cupos": h.cupos_disponibles,
        "responsable": h.responsable
    } for h in horarios]

    return jsonify(data)

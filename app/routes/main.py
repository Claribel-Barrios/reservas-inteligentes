from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import current_user
from flask_mail import Message
from app import mail
from app.models import Servicio, Horario, Reserva
from datetime import date

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    servicios = Servicio.query.filter_by(activo=True).limit(6).all()
    stats = {
        "total_servicios": Servicio.query.filter_by(activo=True).count(),
        "total_reservas": Reserva.query.filter_by(estado="confirmada").count(),
        "total_usuarios": 0,
    }
    return render_template("main/index.html", servicios=servicios, stats=stats)


@main_bp.route("/servicios")
def servicios():

    categoria = request.args.get("categoria")

    query = Servicio.query.filter_by(activo=True)

    todos = query.all()

    categorias = sorted(
        list({s.categoria for s in todos if s.categoria})
    )

    if categoria:

        servicios_categoria = Servicio.query.filter_by(
            activo=True,
            categoria=categoria
        ).all()

        return render_template(
            "main/categoria.html",
            categoria=categoria,
            servicios=servicios_categoria
        )

    return render_template(
        "main/servicios.html",
        categorias=categorias
    )


@main_bp.route('/politica-datos')
def politica_datos():
    return render_template('auth/politica_datos.html')


@main_bp.route('/contacto', methods=['POST'])
def contacto():
    nombre = request.form.get('nombre', '').strip()
    correo = request.form.get('correo', '').strip().lower()
    asunto = request.form.get('asunto', 'Consulta').strip()
    mensaje = request.form.get('mensaje', '').strip()

    if not nombre or not correo or not mensaje:
        flash('Por favor completa todos los campos del formulario de contacto.', 'warning')
        return redirect(url_for('main.index') + '#contacto')

    contacto_info = f"Nombre: {nombre}\nCorreo: {correo}\nAsunto: {asunto}\n\nMensaje:\n{mensaje}"
    recipient = current_app.config.get('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_USERNAME')

    if recipient:
        try:
            msg = Message(subject=f"Contacto web: {asunto}", recipients=[recipient])
            msg.body = contacto_info
            mail.send(msg)
            flash('Gracias por tu mensaje. Nos comunicaremos contigo pronto.', 'success')
        except Exception:
            flash('Tu mensaje fue recibido, pero el correo de salida no está disponible en este momento.', 'info')
    else:
        flash('Tu mensaje fue recibido. Nos comunicaremos contigo pronto.', 'success')

    return redirect(url_for('main.index') + '#contacto')

from flask import url_for, current_app
from flask_mail import Message
from app import mail


def enviar_confirmacion(usuario, reserva):
    msg = Message(
        subject=f"Confirmación de reserva {reserva.codigo}",
        recipients=[usuario.correo]
    )
    horario = reserva.horario
    msg.html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">✅ Reserva Confirmada</h2>
        <p>Hola <strong>{usuario.nombre}</strong>,</p>
        <p>Tu reserva ha sido confirmada exitosamente.</p>
        <div style="background: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <p><strong>Código:</strong> {reserva.codigo}</p>
            <p><strong>Servicio:</strong> {horario.servicio.nombre}</p>
            <p><strong>Fecha:</strong> {horario.fecha.strftime('%d de %B de %Y')}</p>
            <p><strong>Hora:</strong> {horario.hora_inicio.strftime('%H:%M')} - {horario.hora_fin.strftime('%H:%M')}</p>
            <p><strong>Responsable:</strong> {horario.responsable or 'Por asignar'}</p>
        </div>
        <p>Si necesitas cancelar o modificar tu reserva, puedes hacerlo desde tu panel.</p>
    </div>
    """
    mail.send(msg)


def enviar_cancelacion(usuario, reserva):
    msg = Message(
        subject=f"Cancelación de reserva {reserva.codigo}",
        recipients=[usuario.correo]
    )
    msg.html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #dc2626;">❌ Reserva Cancelada</h2>
        <p>Hola <strong>{usuario.nombre}</strong>,</p>
        <p>Tu reserva <strong>{reserva.codigo}</strong> ha sido cancelada.</p>
        <p><strong>Motivo:</strong> {reserva.motivo_cancelacion or 'No especificado'}</p>
        <p>Puedes hacer una nueva reserva desde nuestro sistema.</p>
    </div>
    """
    mail.send(msg)


def enviar_recuperacion(usuario, token):
    from flask import url_for
    enlace = url_for("auth.reset_password", token=token, _external=True)
    msg = Message(
        subject="Recuperación de contraseña",
        recipients=[usuario.correo]
    )
    msg.html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">🔑 Recuperar Contraseña</h2>
        <p>Hola <strong>{usuario.nombre}</strong>,</p>
        <p>Recibimos una solicitud para restablecer tu contraseña.</p>
        <p>
            <a href="{enlace}" style="background: #2563eb; color: white; padding: 12px 24px; 
               border-radius: 6px; text-decoration: none; display: inline-block;">
               Restablecer contraseña
            </a>
        </p>
        <p style="color: #6b7280; font-size: 14px;">Este enlace expira en 2 horas.</p>
        <p style="color: #6b7280; font-size: 14px;">Si no solicitaste esto, ignora este correo.</p>
    </div>
    """
    mail.send(msg)

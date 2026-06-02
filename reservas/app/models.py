from datetime import datetime
from flask_login import UserMixin
from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


class Usuario(db.Model, UserMixin):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    password_hash = db.Column(db.String(200), nullable=False)
    rol = db.Column(db.String(20), default="usuario")  # usuario, admin, empleado
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    token_recuperacion = db.Column(db.String(200))
    token_expira = db.Column(db.DateTime)

    reservas = db.relationship("Reserva", backref="usuario", lazy=True)

    def __repr__(self):
        return f"<Usuario {self.correo}>"

    @property
    def is_admin(self):
        return self.rol == "admin"

    @property
    def is_empleado(self):
        return self.rol in ("admin", "empleado")


class Servicio(db.Model):
    __tablename__ = "servicios"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    duracion_minutos = db.Column(db.Integer, default=60)
    precio = db.Column(db.Float, default=0.0)
    activo = db.Column(db.Boolean, default=True)
    imagen = db.Column(db.String(200))
    categoria = db.Column(db.String(50))

    horarios = db.relationship("Horario", backref="servicio", lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Servicio {self.nombre}>"


class Horario(db.Model):
    __tablename__ = "horarios"

    id = db.Column(db.Integer, primary_key=True)
    servicio_id = db.Column(db.Integer, db.ForeignKey("servicios.id"), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fin = db.Column(db.Time, nullable=False)
    cupos_totales = db.Column(db.Integer, default=1)
    cupos_disponibles = db.Column(db.Integer, default=1)
    responsable = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

    reservas = db.relationship("Reserva", backref="horario", lazy=True)

    def __repr__(self):
        return f"<Horario {self.fecha} {self.hora_inicio}>"

    @property
    def disponible(self):
        return self.cupos_disponibles > 0 and self.activo


class Reserva(db.Model):
    __tablename__ = "reservas"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey("horarios.id"), nullable=False)
    estado = db.Column(db.String(20), default="confirmada")  # confirmada, cancelada, completada, reprogramada
    fecha_reserva = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_cancelacion = db.Column(db.DateTime)
    motivo_cancelacion = db.Column(db.Text)
    notas = db.Column(db.Text)
    codigo = db.Column(db.String(20), unique=True)

    pago = db.relationship("Pago", backref="reserva", uselist=False, lazy=True)

    def __repr__(self):
        return f"<Reserva {self.codigo}>"


class Pago(db.Model):
    __tablename__ = "pagos"

    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey("reservas.id"), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    estado = db.Column(db.String(20), default="pendiente")  # pendiente, exitoso, fallido
    pasarela = db.Column(db.String(50))  # stripe, paypal, payu
    referencia_externa = db.Column(db.String(200))
    fecha_pago = db.Column(db.DateTime)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Pago {self.id} - {self.estado}>"


class Notificacion(db.Model):
    __tablename__ = "notificaciones"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    tipo = db.Column(db.String(50))  # confirmacion, recordatorio, cancelacion, admin
    mensaje = db.Column(db.Text)
    leida = db.Column(db.Boolean, default=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    canal = db.Column(db.String(20), default="sistema")  # sistema, correo, sms

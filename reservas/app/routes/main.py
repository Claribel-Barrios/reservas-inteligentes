from flask import Blueprint, render_template
from flask_login import current_user
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
    categoria = None
    query = Servicio.query.filter_by(activo=True)
    todos = query.all()
    categorias = list({s.categoria for s in todos if s.categoria})
    return render_template("main/servicios.html", servicios=todos, categorias=categorias)

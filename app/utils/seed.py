from datetime import date, time, timedelta
from app import db, bcrypt
from app.models import Usuario, Servicio, Horario


def seed_data():
    """Crea datos iniciales si la base de datos está vacía."""
    if Usuario.query.first():
        return  # Ya hay datos

    # Admin
    admin = Usuario(
        nombre="Administrador",
        correo="admin@reservas.com",
        telefono="3001234567",
        password_hash=bcrypt.generate_password_hash("admin1234").decode("utf-8"),
        rol="admin",
        activo=True
    )
    # Usuario demo
    user = Usuario(
        nombre="María García",
        correo="usuario@demo.com",
        telefono="3109876543",
        password_hash=bcrypt.generate_password_hash("usuario123").decode("utf-8"),
        rol="usuario",
        activo=True
    )
    db.session.add_all([admin, user])

    # Servicios
    servicios = [
        Servicio(
            nombre="Consulta Médica General",
            descripcion="Consulta con médico general para diagnóstico y tratamiento de enfermedades comunes.",
            duracion_minutos=30,
            precio=50000,
            categoria="Salud",
        ),
        Servicio(
            nombre="Sala de Reuniones A",
            descripcion="Sala equipada con proyector, pizarrón y capacidad para 10 personas.",
            duracion_minutos=60,
            precio=80000,
            categoria="Espacios",
        ),
        Servicio(
            nombre="Cancha de Fútbol 5",
            descripcion="Cancha de césped sintético iluminada disponible todos los días.",
            duracion_minutos=60,
            precio=120000,
            categoria="Deportes",
        ),
        Servicio(
            nombre="Asesoría Académica",
            descripcion="Tutorías personalizadas en matemáticas, física y química.",
            duracion_minutos=45,
            precio=35000,
            categoria="Educación",
        ),
        Servicio(
            nombre="Gimnasio - Sesión Personal",
            descripcion="Entrenamiento personalizado con instructor certificado.",
            duracion_minutos=60,
            precio=90000,
            categoria="Deportes",
        ),
        Servicio(
            nombre="Restaurante La Toscana",
            categoria="Restaurantes",
            descripcion="Reserva de mesa para eventos y cenas",
            duracion_minutos=90,
            precio=80000,
            activo=True
        ),
        Servicio(
            nombre="Sushi House",
            categoria="Restaurantes",
            descripcion="Comida japonesa",
            duracion_minutos=90,
            precio=70000,
            activo=True
        ),
        Servicio(
            nombre="Parrilla Colombiana",
            categoria="Restaurantes",
            descripcion="Carnes y parrillas",
            duracion_minutos=90,
            precio=60000,
            activo=True
         )
    ]
    db.session.add_all(servicios)
    db.session.flush()  # Obtener IDs

    # Horarios para los próximos 7 días
    hoy = date.today()
    responsables = ["Dr. Pérez", "Lic. Rodríguez", "Ing. Torres", "Prof. Martínez", "Esp. Ruiz"]
    horas = [(time(8, 0), time(8, 30)), (time(9, 0), time(9, 30)),
             (time(10, 0), time(10, 30)), (time(11, 0), time(11, 30)),
             (time(14, 0), time(14, 30)), (time(15, 0), time(15, 30)),
             (time(16, 0), time(16, 30))]

    for i, servicio in enumerate(servicios):
        for delta in range(1, 8):
            dia = hoy + timedelta(days=delta)
            for j, (hi, hf) in enumerate(horas[:4]):
                horario = Horario(
                    servicio_id=servicio.id,
                    fecha=dia,
                    hora_inicio=hi,
                    hora_fin=hf,
                    cupos_totales=5,
                    cupos_disponibles=5,
                    responsable=responsables[i % len(responsables)],
                    activo=True
                )
                db.session.add(horario)

    db.session.commit()
    print("✅ Datos iniciales creados.")
    print("   Admin: admin@reservas.com / admin1234")
    print("   Usuario: usuario@demo.com / usuario123")

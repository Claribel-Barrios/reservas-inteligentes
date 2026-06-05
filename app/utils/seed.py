from datetime import date, time, timedelta
from app import db, bcrypt
from app.models import Usuario, Servicio, Horario


def seed_data():
    """Crea datos iniciales si la base de datos está vacía."""
    if Usuario.query.first():
        # Si ya hay datos, limpiamos duplicados en todas las categorías.
        servicios_activos = Servicio.query.filter_by(activo=True).order_by(Servicio.id).all()
        seen = set()
        duplicates = []
        for servicio in servicios_activos:
            key = (
                servicio.nombre.strip(),
                servicio.categoria.strip() if servicio.categoria else "",
                servicio.duracion_minutos,
                float(servicio.precio or 0.0)
            )
            if key in seen:
                duplicates.append(servicio)
            else:
                seen.add(key)

        if duplicates:
            for dup in duplicates:
                Horario.query.filter_by(servicio_id=dup.id).delete()
                db.session.delete(dup)
            db.session.commit()
            print("✅ Duplicados eliminados.")

        if Servicio.query.filter_by(categoria="Restaurantes", activo=True).count() == 0:
            restaurantes = [
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
            db.session.add_all(restaurantes)
            db.session.flush()

            hoy = date.today()
            responsables = ["Dr. Pérez", "Lic. Rodríguez", "Ing. Torres", "Prof. Martínez", "Esp. Ruiz"]
            horas = [(time(8, 0), time(8, 30)), (time(9, 0), time(9, 30)),
                     (time(10, 0), time(10, 30)), (time(11, 0), time(11, 30)),
                     (time(14, 0), time(14, 30)), (time(15, 0), time(15, 30)),
                     (time(16, 0), time(16, 30))]

            for i, servicio in enumerate(restaurantes):
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
            print("✅ Restaurantes agregados.")

        additional_services = [
            {
                "nombre": "Cancha de Baloncesto",
                "categoria": "Deportes",
                "descripcion": "Cancha profesional con iluminación y tablero digital.",
                "duracion_minutos": 60,
                "precio": 100000,
            },
            {
                "nombre": "Clases de Yoga",
                "categoria": "Deportes",
                "descripcion": "Sesiones de yoga para todos los niveles.",
                "duracion_minutos": 50,
                "precio": 45000,
            },
            {
                "nombre": "Piscina Olímpica",
                "categoria": "Deportes",
                "descripcion": "Acceso a piscina climatizada y clases de natación.",
                "duracion_minutos": 60,
                "precio": 70000,
            },
            {
                "nombre": "Psicología",
                "categoria": "Salud",
                "descripcion": "Consulta con psicólogo profesional.",
                "duracion_minutos": 50,
                "precio": 65000,
            },
            {
                "nombre": "Fisioterapia",
                "categoria": "Salud",
                "descripcion": "Sesión de rehabilitación y terapia física.",
                "duracion_minutos": 45,
                "precio": 55000,
            },
            {
                "nombre": "Laboratorio Clínico",
                "categoria": "Salud",
                "descripcion": "Toma de muestras y análisis básicos.",
                "duracion_minutos": 30,
                "precio": 40000,
            },
            {
                "nombre": "Clases de Inglés",
                "categoria": "Educación",
                "descripcion": "Clases de inglés conversacional y exámenes.",
                "duracion_minutos": 60,
                "precio": 45000,
            },
            {
                "nombre": "Curso de Programación",
                "categoria": "Educación",
                "descripcion": "Aprende programación básica con proyectos prácticos.",
                "duracion_minutos": 90,
                "precio": 60000,
            },
            {
                "nombre": "Curso de Química",
                "categoria": "Educación",
                "descripcion": "Asesorías en química general y laboratorio.",
                "duracion_minutos": 60,
                "precio": 50000,
            },
            {
                "nombre": "Evento Corporativo",
                "categoria": "Espacios",
                "descripcion": "Sala con capacidad para reuniones empresariales.",
                "duracion_minutos": 180,
                "precio": 150000,
            },
            {
                "nombre": "Taller Creativo",
                "categoria": "Espacios",
                "descripcion": "Espacio para talleres y sesiones de brainstorming.",
                "duracion_minutos": 120,
                "precio": 110000,
            },
            {
                "nombre": "Sesión de Fotografía",
                "categoria": "Espacios",
                "descripcion": "Estudio con iluminación para sesiones fotográficas.",
                "duracion_minutos": 90,
                "precio": 100000,
            },
        ]

        new_services = []
        for spec in additional_services:
            if not Servicio.query.filter_by(nombre=spec["nombre"]).first():
                new_services.append(Servicio(
                    nombre=spec["nombre"],
                    descripcion=spec["descripcion"],
                    duracion_minutos=spec["duracion_minutos"],
                    precio=spec["precio"],
                    categoria=spec["categoria"],
                    activo=True
                ))

        if new_services:
            db.session.add_all(new_services)
            db.session.flush()

            hoy = date.today()
            responsables = ["Dr. Pérez", "Lic. Rodríguez", "Ing. Torres", "Prof. Martínez", "Esp. Ruiz"]
            horas = [(time(8, 0), time(8, 30)), (time(9, 0), time(9, 30)),
                     (time(10, 0), time(10, 30)), (time(11, 0), time(11, 30)),
                     (time(14, 0), time(14, 30)), (time(15, 0), time(15, 30)),
                     (time(16, 0), time(16, 30))]

            for i, servicio in enumerate(new_services):
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
            print("✅ Servicios adicionales agregados.")
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

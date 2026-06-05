from app import create_app
from app.models import Servicio

app = create_app()
with app.app_context():
    servicios = Servicio.query.filter_by(activo=True).all()
    print('TOTAL', len(servicios))
    by_cat = {}
    for s in servicios:
        by_cat.setdefault(s.categoria, []).append(s)
    for cat, items in sorted(by_cat.items()):
        print('\nCATEGORY:', cat, 'count=', len(items))
        seen = set()
        for s in items:
            key = (s.nombre.strip(), s.categoria.strip(), s.precio, s.duracion_minutos)
            dup = key in seen
            print(' DUP' if dup else '    ', repr(s.nombre), s.precio, s.duracion_minutos, s.id)
            seen.add(key)

from app import create_app
from app.models import Servicio
from app.utils.seed import seed_data

app = create_app()
with app.app_context():
    seed_data()
    restos = Servicio.query.filter(Servicio.categoria == 'Restaurantes').all()
    print('count', len(restos))
    for s in restos:
        print(repr(s.nombre), s.precio, s.activo)

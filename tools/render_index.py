from jinja2 import Environment, FileSystemLoader
from types import SimpleNamespace
import sys
env=Environment(loader=FileSystemLoader('app/templates'))
env.globals['url_for'] = lambda endpoint, filename=None: f"/static/{filename}" if filename else '/'
env.globals['get_flashed_messages'] = lambda with_categories=False: []
ctx={
 'current_user': SimpleNamespace(is_authenticated=False, is_admin=False),
 'stats': SimpleNamespace(total_servicios=5, total_reservas=123),
 'servicios': [SimpleNamespace(categoria='Salud', nombre='Consulta', descripcion='Descripción de ejemplo', duracion_minutos=30, precio=100, id=1)]
}
rendered = env.get_template('main/index.html').render(**ctx)
open('tools/rendered_index.html','w', encoding='utf-8').write(rendered)
print('WROTE')

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from flask import current_app, render_template

# Use FRONTEND_URL from env if present, otherwise set an example
frontend = os.environ.get('FRONTEND_URL', 'https://abc123.ngrok.io')
app = create_app()
with app.app_context():
    token = 'ejemplo-token-123'
    base = current_app.config.get('FRONTEND_URL') or frontend
    # Build path manually to avoid url_for requirement for SERVER_NAME outside requests
    path = f"/reset/{token}"
    enlace = base.rstrip('/') + path
    codigo = '123456'
    html = render_template('emails/recuperacion_password.html', codigo=codigo)
    print('Enlace generado:')
    print(enlace)
    print('\n--- HTML del correo (preview) ---\n')
    print(html)

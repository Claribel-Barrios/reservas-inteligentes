import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from flask import url_for, current_app

# Use FRONTEND_URL from env if present, otherwise set an example
frontend = os.environ.get('FRONTEND_URL', 'https://abc123.ngrok.io')
app = create_app()
with app.app_context():
    token = 'ejemplo-token-123'
    base = current_app.config.get('FRONTEND_URL') or frontend
    # Build path manually to avoid url_for requirement for SERVER_NAME outside requests
    path = f"/reset/{token}"
    enlace = base.rstrip('/') + path
    html = f'''<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">🔑 Recuperar Contraseña</h2>
        <p>Hola <strong>Usuario Ejemplo</strong>,</p>
        <p>Recibimos una solicitud para restablecer tu contraseña.</p>
        <p>
            <a href="{enlace}" style="background: #2563eb; color: white; padding: 12px 24px; 
               border-radius: 6px; text-decoration: none; display: inline-block;">
               Restablecer contraseña
            </a>
        </p>
        <p style="color: #6b7280; font-size: 14px;">Este enlace expira en 2 horas.</p>
        <p style="color: #6b7280; font-size: 14px;">Si no solicitaste esto, ignora este correo.</p>
    </div>'''
    print('Enlace generado:')
    print(enlace)
    print('\n--- HTML del correo (preview) ---\n')
    print(html)

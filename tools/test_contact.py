import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from flask import get_flashed_messages

app = create_app()
app.config['TESTING'] = True
# Ensure Flask-Mail won't actually send emails
app.config['MAIL_SUPPRESS_SEND'] = True
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@example.com'

with app.test_client() as client:
    data = {
        'nombre': 'Prueba',
        'correo': 'prueba@example.com',
        'asunto': 'Consulta de prueba',
        'mensaje': 'Este es un mensaje de prueba desde el entorno local.'
    }
    resp = client.post('/contacto', data=data, follow_redirects=True)
    print('status_code:', resp.status_code)
    body = resp.get_data(as_text=True)
    # print a short snippet searching for expected flash text
    if 'Gracias por tu mensaje' in body:
        print('Flash: Gracias por tu mensaje (success)')
    elif 'Tu mensaje fue recibido' in body:
        print('Flash: Tu mensaje fue recibido')
    elif 'Por favor completa todos los campos' in body:
        print('Flash: falta completar campos')
    else:
        print('No expected flash found; response length:', len(body))
    # Optionally print first 800 chars of body for inspection
    print('\n--- response snippet ---\n')
    print(body[:800])

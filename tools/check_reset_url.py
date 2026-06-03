import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from flask import url_for

app = create_app()
with app.app_context():
    print(url_for('auth.reset_password', token='deadbeef', _external=True))

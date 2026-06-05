import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "clave-secreta-reservas-2024"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "reservas.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = "reservasinteligentes9@gmail.com"
    MAIL_PASSWORD = "pbqqyjfykrozkzxi"
    MAIL_DEFAULT_SENDER = ("Sistema de Reservas", os.environ.get("MAIL_USERNAME", "reservasinteligentes9@gmail.com"))

    # External URL used to build absolute links in emails (useful for ngrok or deployed host)
    # Example: https://mi-dominio.com or https://abc123.ngrok.io
    FRONTEND_URL = os.environ.get("FRONTEND_URL")
    PREFERRED_URL_SCHEME = os.environ.get("PREFERRED_URL_SCHEME", "http")

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # Pagination
    ITEMS_PER_PAGE = 10

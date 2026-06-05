from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import mail
from datetime import datetime, timedelta
import secrets
from app import db, bcrypt
from app.models import Usuario
from app.utils.email import enviar_recuperacion

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        telefono = request.form.get("telefono", "").strip()
        password = request.form.get("password", "")
        confirmar = request.form.get("confirmar_password", "")

        errores = []
        if not nombre:
            errores.append("El nombre es obligatorio.")
        if not correo:
            errores.append("El correo es obligatorio.")
        if len(password) < 8:
            errores.append("La contraseña debe tener al menos 8 caracteres.")
        if password != confirmar:
            errores.append("Las contraseñas no coinciden.")
        if Usuario.query.filter_by(correo=correo).first():
            errores.append("Ya existe una cuenta con ese correo.")

        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template("auth/registro.html")

        hash_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        usuario = Usuario(nombre=nombre, correo=correo, telefono=telefono, password_hash=hash_pw)
        db.session.add(usuario)
        db.session.commit()

        flash("¡Cuenta creada exitosamente! Ya puedes iniciar sesión.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/registro.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()
        password = request.form.get("password", "")
        recordar = request.form.get("recordar") == "on"

        usuario = Usuario.query.filter_by(correo=correo).first()

        if usuario and usuario.activo and bcrypt.check_password_hash(usuario.password_hash, password):
            login_user(usuario, remember=recordar)
            next_page = request.args.get("next")
            flash(f"¡Bienvenido, {usuario.nombre}!", "success")
            if usuario.is_admin:
                return redirect(next_page or url_for("admin.dashboard"))
            return redirect(next_page or url_for("main.index"))

        error = "Correo electrónico o contraseña incorrectos."
        flash("Correo o contraseña incorrectos.", "danger")

    return render_template("auth/login.html", error=error)


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/recuperar", methods=["GET", "POST"])
def recuperar():
    error = None
    success = None

    if request.method == "POST":
        correo = request.form.get("correo", "").strip().lower()

        usuario = Usuario.query.filter_by(correo=correo).first()

        success = "Si el correo está registrado, recibirás instrucciones para recuperar tu contraseña."

        if usuario:
            try:
                token = secrets.token_urlsafe(32)
                usuario.token_recuperacion = token
                usuario.token_expira = datetime.utcnow() + timedelta(hours=1)
                db.session.commit()

                enlace = url_for("auth.reset_password", token=token, _external=True)

                msg = Message(
                    subject="Recuperación de contraseña",
                    recipients=[usuario.correo]
                )

                msg.html = f"""
                Recuperación de contraseña

                Hola {usuario.nombre},

                Haz clic en el siguiente enlace para cambiar tu contraseña:

                [Restablecer contraseña]({enlace})

                Este enlace expirará en 1 hora.
                """

                mail.send(msg)
                print("Correo enviado")

            except Exception as e:
                print("ERROR:")
                print(e)
                error = "Ocurrió un error al enviar el correo."

        return render_template("auth/recuperar.html", success=success, error=error)

    return render_template("auth/recuperar.html")


@auth_bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    usuario = Usuario.query.filter_by(token_recuperacion=token).first()

    if not usuario or (usuario.token_expira and usuario.token_expira < datetime.utcnow()):
        flash("El enlace es inválido o ha expirado.", "danger")
        return redirect(url_for("auth.recuperar"))

    if request.method == "POST":
        password = request.form.get("password", "")
        confirmar = request.form.get("confirmar_password", "")

        if len(password) < 8:
            flash("La contraseña debe tener al menos 8 caracteres.", "danger")
        elif password != confirmar:
            flash("Las contraseñas no coinciden.", "danger")
        else:
            usuario.password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
            usuario.token_recuperacion = None
            usuario.token_expira = None
            db.session.commit()
            flash("Contraseña actualizada exitosamente.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html")


@auth_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        telefono = request.form.get("telefono", "").strip()
        nueva_pw = request.form.get("nueva_password", "")
        confirmar = request.form.get("confirmar_password", "")

        if nombre:
            current_user.nombre = nombre
        if telefono:
            current_user.telefono = telefono

        if nueva_pw:
            if len(nueva_pw) < 8:
                flash("La contraseña debe tener al menos 8 caracteres.", "danger")
                return render_template("auth/perfil.html")
            if nueva_pw != confirmar:
                flash("Las contraseñas no coinciden.", "danger")
                return render_template("auth/perfil.html")
            current_user.password_hash = bcrypt.generate_password_hash(nueva_pw).decode("utf-8")

        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")

    return render_template("auth/perfil.html")

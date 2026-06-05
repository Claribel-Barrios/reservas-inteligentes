from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
from app import mail
from datetime import datetime, timedelta
import random
import secrets
from app import db, bcrypt
from app.models import Usuario, RecuperacionPassword

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
        acepta_politica = request.form.get("acepta_politica")

        errores = []
        if not acepta_politica:
            errores.append("Debes aceptar la Política de Tratamiento de Datos para registrarte.")
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
        session.permanent = True

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
    session.clear()
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
                codigo = f"{random.randint(100000, 999999)}"
                expira = datetime.utcnow() + timedelta(minutes=10)

                usuario.token_recuperacion = token
                usuario.token_expira = datetime.utcnow() + timedelta(hours=1)
                db.session.add(RecuperacionPassword(usuario_id=usuario.id, codigo=codigo, fecha_expiracion=expira))
                db.session.commit()

                session["reset_token"] = token
                session["codigo_recuperacion"] = codigo
                session["codigo_expiracion"] = expira.isoformat()

                msg = Message(
                    subject="Recuperación de contraseña",
                    recipients=[usuario.correo]
                )

                html = render_template("emails/recuperacion_password.html", codigo=codigo)
                msg.html = html

                mail.send(msg)
                flash("Hemos enviado un código de verificación a tu correo.", "info")
                return redirect(url_for("auth.verificar_codigo"))

            except Exception as e:
                print("ERROR:")
                print(e)
                error = "Ocurrió un error al enviar el correo."

        return render_template("auth/recuperar.html", success=success, error=error)

    return render_template("auth/recuperar.html")


@auth_bp.route("/verificar-codigo", methods=["GET", "POST"])
def verificar_codigo():
    if request.method == "POST":
        codigo = request.form.get("codigo", "").strip()
        codigo_guardado = session.get("codigo_recuperacion")
        fecha_expiracion = session.get("codigo_expiracion")

        if codigo == codigo_guardado and datetime.fromisoformat(fecha_expiracion) > datetime.utcnow():

            session.pop("codigo_recuperacion", None)
            session.pop("codigo_expiracion", None)

            flash("Código verificado correctamente.", "success")

            return redirect(
                url_for(
                    "auth.nueva_password",
                    token=session.get("reset_token", "")
                )
            )

        flash("El código ingresado no es válido o ha expirado.", "danger")
        return render_template("auth/verificar_codigo.html")

    return render_template("auth/verificar_codigo.html")


@auth_bp.route("/reset/<token>", methods=["GET", "POST"])
def nueva_password(token):
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
            session.pop("reset_token", None)
            session.pop("codigo_recuperacion", None)
            session.pop("codigo_expiracion", None)  
            flash("Contraseña actualizada exitosamente.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/nueva_password.html")


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

@auth_bp.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

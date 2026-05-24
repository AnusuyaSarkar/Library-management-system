from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from .. import db
from ..models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not username or not email or len(password) < 6:
            flash("Provide valid details. Password must be at least 6 chars.", "danger")
            return render_template("register.html")

        exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if exists:
            flash("Username or email already exists.", "warning")
            return render_template("register.html")

        user = User(username=username, email=email, role="manager")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        login_as = request.form.get("login_as", "user").strip().lower()
        if login_as not in {"admin", "user"}:
            login_as = "user"
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            # Accept both legacy and current non-admin role names as user.
            effective_role = "user" if user.role in {"user", "manager"} else user.role
            if effective_role != login_as:
                flash(f"This account is not a {login_as} account.", "warning")
                return render_template("login.html")
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

from __future__ import annotations

from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if (
            username == current_app.config.get("ADMIN_USERNAME")
            and password == current_app.config.get("ADMIN_PASSWORD")
        ):
            session["admin_logged_in"] = True
            flash("Logged in successfully.", "success")
            next_url = request.args.get("next")
            return redirect(next_url or url_for("items.list_items"))
        else:
            flash("Invalid credentials.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout", methods=["POST"])  # logout via POST for safety
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))

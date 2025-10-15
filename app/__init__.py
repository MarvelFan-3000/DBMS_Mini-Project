import os
from flask import Flask, redirect, url_for

from .config import Config
from .extensions import db, migrate

def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True, static_folder="static", template_folder="templates")
    # Ensure instance folder exists for SQLite default or other instance files
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints
    from .auth import auth_bp
    from .items import items_bp
    from .reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(items_bp)
    app.register_blueprint(reports_bp)

    @app.route("/")
    def index():
        return redirect(url_for("items.list_items"))

    # Create tables if they don't exist (useful for SQLite dev and first run)
    with app.app_context():
        db.create_all()

    return app

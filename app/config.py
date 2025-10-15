import os
from pathlib import Path


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # Prefer DATABASE_URL env (e.g., mysql+pymysql://user:pass@host:3306/dbname)
    # Fallback to SQLite for local/dev convenience
    default_sqlite_path = Path(os.environ.get("SQLITE_PATH", "instance/app.db")).absolute()
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or f"sqlite:///{default_sqlite_path}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Simple admin credentials for demo purposes
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

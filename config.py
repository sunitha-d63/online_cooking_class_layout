import os
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.resolve()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY") or "dev-secret-change-me"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or f"sqlite:///{PROJECT_DIR/'app.db'}"

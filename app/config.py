import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    DEBUG = False
    SQLITE_DB_DIR = None
    SQLALCHEMY_DATABASE_URI = None
    SECRET_KEY = None
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class LocalDevelopmentConfig(Config):
    SQLITE_DB_DIR = os.path.join(basedir, "database")
    os.makedirs(SQLITE_DB_DIR, exist_ok=True)

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(SQLITE_DB_DIR, "sih.sqlite3")

    SECRET_KEY = "sih_key"

    JWT_SECRET_KEY = "super-secret-jwt-key"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

    JWT_TOKEN_LOCATION = ["headers"]  # noqa: RUF012
    JWT_HEADER_TYPE = "Bearer"

    DEBUG = True
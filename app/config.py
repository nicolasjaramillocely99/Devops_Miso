import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5433/blacklist_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_TOKEN = os.environ.get("STATIC_TOKEN", "default-dev-token")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-key")


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL_TEST", "postgresql://postgres:postgres@localhost:5433/blacklist_test_db"
    )
    STATIC_TOKEN = "test-static-token"

import pytest
from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    return app


@pytest.fixture(autouse=True)
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    return {
        "Authorization": "Bearer test-static-token",
        "Content-Type": "application/json",
    }

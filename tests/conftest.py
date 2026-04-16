import pytest
from app import create_app


@pytest.fixture(scope="session")
def app():
    app = create_app("testing")
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers():
    return {
        "Authorization": "Bearer test-static-token",
        "Content-Type": "application/json",
    }

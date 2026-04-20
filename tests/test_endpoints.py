"""
Pruebas unitarias - una por cada endpoint de la API del microservicio Blacklist.

Stack: pytest + unittest.mock (biblioteca estandar de Python).
No requieren motor de BD real: las operaciones de SQLAlchemy se mockean.
"""
from unittest.mock import patch, MagicMock


def test_health_endpoint_returns_ok(client):
    # Prueba positiva: Verifica que el endpoint de salud responda correctamente sin autenticación
    """GET /health -> 200 con payload de estado."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy", "version": "1.0.4"}


@patch("app.resources.blacklist.db.session")
def test_post_blacklist_creates_entry(mock_session, client, auth_headers):
    # Prueba positiva: Verifica que se pueda agregar un email a la lista negra con datos válidos y auth
    """POST /blacklists -> 201 e invoca db.session.add y db.session.commit una vez."""
    payload = {
        "email": "user@test.com",
        "app_uuid": "11111111-1111-1111-1111-111111111111",
        "blocked_reason": "spam",
    }

    response = client.post("/blacklists", headers=auth_headers, json=payload)

    assert response.status_code == 201
    assert response.get_json() == {
        "message": "Email agregado a la lista negra exitosamente"
    }
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()


@patch("app.resources.blacklist.BlacklistEntry")
def test_get_blacklist_returns_status(mock_entry, client, auth_headers):
    # Prueba positiva: Verifica que se pueda consultar un email bloqueado y devuelva el estado correcto
    """GET /blacklists/<email> -> 200 con is_blacklisted=True cuando el registro existe."""
    fake_entry = MagicMock(blocked_reason="spam")
    mock_entry.query.filter_by.return_value.first.return_value = fake_entry

    response = client.get("/blacklists/user@test.com", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {
        "is_blacklisted": True,
        "blocked_reason": "spam",
    }
    mock_entry.query.filter_by.assert_called_once_with(email="user@test.com")
@patch("app.resources.blacklist.BlacklistEntry")
def test_get_blacklist_returns_not_blacklisted(mock_entry, client, auth_headers):
    # Prueba positiva/alternativa: Verifica que se pueda consultar un email no bloqueado y devuelva el estado correcto
    """GET /blacklists/<email> -> 200 con is_blacklisted=False cuando no existe registro."""
    mock_entry.query.filter_by.return_value.first.return_value = None

    response = client.get("/blacklists/user@test.com", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {
        "is_blacklisted": False,
        "blocked_reason": "",
    }
    mock_entry.query.filter_by.assert_called_once_with(email="user@test.com")


def test_post_blacklist_requires_auth(client):
    # Prueba negativa: Verifica que el endpoint requiera autenticación y devuelva error 401 sin token
    """POST /blacklists -> 401 sin token de auth."""
    payload = {
        "email": "user@test.com",
        "app_uuid": "11111111-1111-1111-1111-111111111111",
    }

    response = client.post("/blacklists", json=payload)

    assert response.status_code == 401
    assert "Token de autorizacion requerido" in response.get_json()["message"]

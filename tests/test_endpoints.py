"""
Pruebas unitarias - una por cada endpoint de la API del microservicio Blacklist.

Stack: pytest + unittest.mock (biblioteca estandar de Python).
No requieren motor de BD real: las operaciones de SQLAlchemy se mockean.
"""
from unittest.mock import patch, MagicMock


def test_health_endpoint_returns_ok(client):
    """GET /health -> 200 con payload de estado."""
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy", "version": "1.0.4"}


@patch("app.resources.blacklist.db.session")
def test_post_blacklist_creates_entry(mock_session, client, auth_headers):
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

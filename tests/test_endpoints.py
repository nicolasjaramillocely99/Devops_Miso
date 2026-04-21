from unittest.mock import MagicMock, patch


def test_health_endpoint_returns_ok(client):
    # Prueba positiva: el endpoint de salud responde correctamente sin token.
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "healthy", "version": "1.0.4"}


@patch("app.resources.blacklist.db.session")
def test_post_blacklist_creates_entry(mock_session, client, auth_headers):
    # Prueba positiva: crea un registro en blacklist con token y datos validos.
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
def test_get_blacklist_returns_true_when_email_exists(mock_entry, client, auth_headers):
    # Prueba positiva: consulta un email existente en la blacklist.
    fake_entry = MagicMock(blocked_reason="spam")
    mock_entry.query.filter_by.return_value.first.return_value = fake_entry

    response = client.get("/blacklists/user@test.com", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {"is_blacklisted": True, "blocked_reason": "spam"}
    mock_entry.query.filter_by.assert_called_once_with(email="user@test.com")


@patch("app.resources.blacklist.BlacklistEntry")
def test_get_blacklist_returns_false_when_email_does_not_exist(
    mock_entry, client, auth_headers
):
    # Prueba positiva: consulta un email valido que no esta en la blacklist.
    mock_entry.query.filter_by.return_value.first.return_value = None

    response = client.get("/blacklists/missing@test.com", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {"is_blacklisted": False, "blocked_reason": ""}
    mock_entry.query.filter_by.assert_called_once_with(email="missing@test.com")


def test_post_blacklist_requires_auth(client):
    # Prueba negativa: rechaza la creacion cuando no se envia token.
    payload = {
        "email": "user@test.com",
        "app_uuid": "11111111-1111-1111-1111-111111111111",
    }

    response = client.post("/blacklists", json=payload)

    assert response.status_code == 401
    assert "Token de autorizacion requerido" in response.get_json()["message"]

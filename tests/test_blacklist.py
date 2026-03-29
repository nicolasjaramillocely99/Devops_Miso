import json


def test_post_blacklist_success(client, auth_headers):
    """Positivo: agregar email a la lista negra retorna 201."""
    response = client.post(
        "/blacklists",
        data=json.dumps({
            "email": "spam@example.com",
            "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "blocked_reason": "Envio de spam recurrente",
        }),
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = json.loads(response.data)
    assert "exitosamente" in data["message"]


def test_get_blacklisted_email_returns_true(client, auth_headers):
    """Positivo: consultar un email que esta en la lista negra retorna is_blacklisted=true."""
    client.post(
        "/blacklists",
        data=json.dumps({
            "email": "blocked@example.com",
            "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
            "blocked_reason": "Fraude",
        }),
        headers=auth_headers,
    )

    response = client.get(
        "/blacklists/blocked@example.com",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["is_blacklisted"] is True
    assert data["blocked_reason"] == "Fraude"


def test_post_blacklist_without_token_returns_401(client):
    """Negativo: enviar POST sin token de autorizacion retorna 401."""
    response = client.post(
        "/blacklists",
        data=json.dumps({
            "email": "test@example.com",
            "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
        }),
        content_type="application/json",
    )
    assert response.status_code == 401


def test_post_blacklist_missing_email_returns_400(client, auth_headers):
    """Negativo: enviar POST sin el campo email retorna 400."""
    response = client.post(
        "/blacklists",
        data=json.dumps({
            "app_uuid": "550e8400-e29b-41d4-a716-446655440000",
        }),
        headers=auth_headers,
    )
    assert response.status_code == 400

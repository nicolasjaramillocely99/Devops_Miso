from functools import wraps
from flask import request, jsonify, current_app


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return {"message": "Token de autorizacion requerido"}, 401

        parts = auth_header.split(" ")
        if len(parts) != 2 or parts[0] != "Bearer":
            return {"message": "Formato de token invalido. Use: Bearer <token>"}, 401

        token = parts[1]
        if token != current_app.config["STATIC_TOKEN"]:
            return {"message": "Token invalido o expirado"}, 401

        return f(*args, **kwargs)

    return decorated

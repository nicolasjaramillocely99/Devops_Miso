from flask import request
from flask_restful import Resource
from app import db
from app.models import BlacklistEntry
from app.schemas import BlacklistCreateSchema
from app.auth import token_required

blacklist_schema = BlacklistCreateSchema()


class BlacklistResource(Resource):
    method_decorators = [token_required]

    def post(self):
        json_data = request.get_json(silent=True)
        if not json_data:
            return {"message": "El cuerpo de la solicitud debe ser JSON"}, 400

        errors = blacklist_schema.validate(json_data)
        if errors:
            return {"message": "Datos invalidos", "errors": errors}, 400

        data = blacklist_schema.load(json_data)

        ip_address = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
        if "," in ip_address:
            ip_address = ip_address.split(",")[0].strip()

        entry = BlacklistEntry(
            email=data["email"],
            app_uuid=data["app_uuid"],
            blocked_reason=data.get("blocked_reason"),
            ip_address=ip_address,
        )

        db.session.add(entry)
        db.session.commit()

        return {"message": "Email agregado a la lista negra exitosamente"}, 201


class BlacklistQueryResource(Resource):
    method_decorators = [token_required]

    def get(self, email):
        entry = BlacklistEntry.query.filter_by(email=email).first()

        if entry:
            return {
                "is_blacklisted": True,
                "blocked_reason": entry.blocked_reason or "",
            }, 200

        return {
            "is_blacklisted": False,
            "blocked_reason": "",
        }, 200

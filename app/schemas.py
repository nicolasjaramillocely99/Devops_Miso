from marshmallow import Schema, fields, validate


class BlacklistCreateSchema(Schema):
    email = fields.String(required=True)
    app_uuid = fields.String(required=True)
    blocked_reason = fields.String(
        load_default=None, validate=validate.Length(max=255)
    )

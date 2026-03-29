from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
ma = Marshmallow()


def create_app(config_name=None):
    app = Flask(__name__)

    if config_name == "testing":
        from app.config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from app.config import Config
        app.config.from_object(Config)

    db.init_app(app)
    ma.init_app(app)
    JWTManager(app)

    api = Api(app)

    from app.resources.blacklist import BlacklistResource, BlacklistQueryResource
    from app.resources.health import HealthResource

    api.add_resource(BlacklistResource, "/blacklists")
    api.add_resource(BlacklistQueryResource, "/blacklists/<string:email>")
    api.add_resource(HealthResource, "/health")

    with app.app_context():
        db.create_all()

    return app

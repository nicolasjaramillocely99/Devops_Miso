from flask_restful import Resource


class HealthResource(Resource):
    def get(self):
        result = {
            "status": "healthy",
            "version": "1.0.4"
        }
        return result, 200

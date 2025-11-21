from flask.views import MethodView
from flask_smorest import Blueprint
from flask_jwt_extended import jwt_required

blp = Blueprint("test", __name__, description="Test endpoints")

@blp.route("/guest")
class TestGuestEndpoint(MethodView):
    @blp.response(200, description="Guest endpoint accessed successfully.")
    def get(self):
        return {"message": "This endpoint is open to everyone."}

@blp.route("/protected")
class TestAuthEndpoint(MethodView):
    @jwt_required()
    @blp.response(200, description="Protected endpoint accessed successfully.")
    @blp.alt_response(401, description="Missing or invalid token.")
    def get(self):
        return {"message": "This is a protected endpoint."}
    
@blp.route("/fresh-protected")
class TestFreshAuthEndpoint(MethodView):
    @jwt_required(fresh=True)
    @blp.response(200, description="Fresh protected endpoint accessed successfully.")
    @blp.alt_response(401, description="Missing or invalid fresh token.")
    def get(self):
        return {"message": "This is a protected endpoint. You used a fresh token to access it."}
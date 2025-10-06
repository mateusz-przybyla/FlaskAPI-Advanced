from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required

blp = Blueprint("test", __name__, description="Test endpoints")

@blp.route("/guest")
class TestGuestEndpoint(MethodView):
    def get(self):
        return {"message": "This endpoint is open to everyone."}

@blp.route("/protected")
class TestAuthEndpoint(MethodView):
    @jwt_required()
    def get(self):
        return {"message": "This is a protected endpoint."}
    
@blp.route("/fresh-protected")
class TestFreshAuthEndpoint(MethodView):
    @jwt_required(fresh=True)
    def get(self):
        return {"message": "This is a protected endpoint. You used a fresh token to access it."}

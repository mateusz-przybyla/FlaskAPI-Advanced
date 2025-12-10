from flask import current_app
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from api.extensions import db, email_queue
from api.models import UserModel
from api.schemas import UserSchema, UserRegisterSchema
from api.services.blocklist import add_jti_to_blocklist
from api.tasks.email_tasks import send_user_registration_email

blp = Blueprint("user", __name__, description="Endpoints for user registration, authentication and account management")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, description="User created successfully.")
    @blp.alt_response(409, description="A user with that email already exists.")
    def post(self, user_data: dict[str, str]) -> dict[str, str]:
        if UserModel.query.filter(UserModel.email == user_data['email']).first():
            abort(409, message="A user with that email already exists.")

        user = UserModel(
            username=user_data['username'],
            email=user_data['email'],
            password=sha256.hash(user_data['password'])
        )

        try:
            db.session.add(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while creating the user.")

        try:
            email_queue.enqueue(send_user_registration_email, user.email, user.username)
        except Exception as e:
            current_app.logger.error(f"Failed to enqueue email task: {e}")

        return {"message": "User created successfully."}
        
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200, description="User logged in successfully.")
    @blp.alt_response(401, description="Invalid credentials.")
    def post(self, user_data: dict[str, str]) -> dict[str, str]:
        user = UserModel.query.filter(UserModel.email == user_data['email']).first()

        if user and sha256.verify(user_data['password'], user.password):
            access_token = create_access_token(identity=str(user.id), fresh=True)
            refresh_token = create_refresh_token(identity=str(user.id))
            return {"access_token": access_token, "refresh_token": refresh_token}

        abort(401, message="Invalid credentials.")

@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200, description="User logged out successfully.")
    def post(self) -> dict[str, str]:
        jti = get_jwt()['jti']
        exp = get_jwt()['exp'] - datetime.now(timezone.utc).timestamp()
        add_jti_to_blocklist(jti, int(exp))
        return {"message": "Successfully logged out."}
    
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200, description="Access token refreshed successfully.")
    def post(self) -> dict[str, str]:
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}

@blp.route("/users/me")
class UserMe(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema, description="Authenticated user's profile.")
    def get(self) -> UserModel:
        user_id = get_jwt_identity()
        user = db.session.get(UserModel, user_id) or abort(404)
        return user
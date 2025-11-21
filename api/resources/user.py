from flask import current_app
from flask.views import MethodView
from flask_smorest import abort, Blueprint
from passlib.hash import pbkdf2_sha256 as sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from api.extensions import db
from api.models import UserModel
from api.schemas import UserSchema, UserRegisterSchema
from api.services.blocklist import add_jti_to_blocklist, is_jti_blocked
from api.workers.mail_worker import send_user_registration_email

blp = Blueprint("user", __name__, description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, description="User created successfully.")
    @blp.alt_response(409, description="A user with that email already exists.")
    def post(self, user_data):
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
            current_app.email_queue.enqueue(
                send_user_registration_email,   
                user.email,
                user.username   
            )
        except Exception as e:
            current_app.logger.error(f"Failed to enqueue email task: {e}")

        return {"message": "User created successfully."}
        
@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200, description="User logged in successfully.")
    @blp.alt_response(401, description="Invalid credentials.")
    def post(self, user_data):
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
    def post(self):
        jti = get_jwt()['jti']
        exp = get_jwt()['exp'] - datetime.now(timezone.utc).timestamp()
        add_jti_to_blocklist(jti, int(exp))

        # For debugging purposes
        # print(is_jti_blocked(jti))

        return {"message": "Successfully logged out."}
    
@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200, description="Access token refreshed successfully.")
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)
        return {"access_token": new_token}

# dev endpoints to view and delete users    
@blp.route("/user/<int:user_id>")
class User(MethodView):
    @blp.response(200, UserSchema, description="User details retrieved successfully.")
    @blp.alt_response(404, description="User not found.")
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user
    
    @blp.response(200, description="User deleted successfully.")
    @blp.alt_response(404, description="User not found.")
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)

        try:
            db.session.delete(user)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while deleting the user.")

        return {"message": "User deleted."}